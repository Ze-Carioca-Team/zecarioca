#!/usr/bin/env python
# coding=utf-8
import sys
import json
import math
import torch
import wandb
import logging
import argparse
from tqdm import tqdm
from copy import deepcopy
from dialogparser import parser, remove_tags
from metrics import compute
from torch.utils.data import Dataset, DataLoader
from transformers import (
    GPT2Tokenizer, GPT2LMHeadModel,
    default_data_collator,
    AdamW,
    get_scheduler,
    SchedulerType
)
from datasets import load_dataset, load_metric

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def parse_args():
    parser = argparse.ArgumentParser(description="Finetune a transformers "
                                    "model on a causal language modeling task")
    parser.add_argument("--project_name", type=str, help="Wandb project name.")
    parser.add_argument("--run_name", type=str, help="Wandb run name.")
    parser.add_argument("--run_id", type=str, help="Wandb run id.")
    parser.add_argument("--directory", type=str, help="A path to save model.")
    parser.add_argument("--checkpoint", type=str,
        default="models/adrenaline_multiwoz/epoch56_trloss0.40_gpt2",
        help="A path for initial model.")
    parser.add_argument("--initial_epoch", type=int, default=0,
        help="Initial training epoch.")
    parser.add_argument("--batch_size", type=int, default=8,
        help="Size of the batch.")
    parser.add_argument("--resume_path", type=str, default=None,
        help="Checkpoint address for continuing training.")
    parser.add_argument("--train_file", type=str, default="data/process.train.json",
        help="A json file containing the training data.")
    parser.add_argument("--validation_file", type=str, default="data/process.valid.json",
        help="A json file containing the validation data.")
    parser.add_argument("--learning_rate", type=float, default=2e-5,
        help="Initial learning rate to use.")
    parser.add_argument("--weight_decay", type=float, default=0.01,
        help="Weight decay to use.")
    parser.add_argument("--num_train_epochs", type=int, default=None,
        help="Total number of training epochs to perform.")
    parser.add_argument("--max_train_steps", type=int, default=None,
        help="Total number of training steps to perform.")
    parser.add_argument("--gradient_accumulation_steps", type=int, default=32,
        help="Number of updates steps to accumulate for a backward/update pass.")
    parser.add_argument("--lr_scheduler_type", type=SchedulerType, default="linear",
        help="The scheduler type to use.", choices=["linear", "cosine",
        "cosine_with_restarts", "polynomial", "constant", "constant_with_warmup"])
    parser.add_argument("--num_warmup_steps", type=int, default=1,
        help="Number of steps for the warmup in the lr scheduler.")
    return parser.parse_args()

def main():
    args = parse_args()

    if (args.initial_epoch != 0): wandb.init(id=args.run_id, project=args.project_name, resume=True)
    else:
        wandb.init(project=args.project_name)
        wandb.run.name = args.run_name
        wandb.config.update(args)
        wandb.run.save()

    with open("data/ontology.json") as fin:
        tokens = json.load(fin)

    tokenizer = GPT2Tokenizer.from_pretrained(args.checkpoint)
    model = GPT2LMHeadModel.from_pretrained(args.checkpoint)
    if (args.initial_epoch == 0):
        tokenizer.added_tokens_encoder = {}
        tokenizer.added_tokens_dencoder = {}
        tokenizer.add_special_tokens({"additional_special_tokens": tokens})
        tokenizer.pad_token = tokenizer.eos_token
    model.resize_token_embeddings(len(tokenizer))
    datasets = load_dataset("json", data_files={"train":args.train_file,
                                                "valid":args.validation_file})
    def add_tokens(examples):
        res = tokenizer(examples['text'], max_length=256, truncation=True,
                        padding='max_length')
        res['labels'] = deepcopy(res['input_ids'])
        return res

    tokenized = datasets.map(add_tokens, num_proc=4, batched=True,
                             batch_size=args.batch_size,
                             remove_columns=["id", "text"])

    train_dataset = tokenized["train"]
    valid_dataset = tokenized["valid"]
    train_dataloader = DataLoader(
        train_dataset, shuffle=True, batch_size=args.batch_size,
        collate_fn=default_data_collator
    )
    valid_dataloader = DataLoader(
        valid_dataset, batch_size=args.batch_size,
        collate_fn=default_data_collator
    )
    no_decay = ["bias", "LayerNorm.weight"]
    optimizer_grouped_parameters = [
        {
            "params": [p for n, p in model.named_parameters() if not any(nd in n for nd in no_decay)],
            "weight_decay": args.weight_decay,
        },
        {
            "params": [p for n, p in model.named_parameters() if any(nd in n for nd in no_decay)],
            "weight_decay": 0.0,
        },
    ]
    optimizer = AdamW(optimizer_grouped_parameters, lr=args.learning_rate)

    num_update_steps_per_epoch = math.ceil(len(train_dataloader) / args.gradient_accumulation_steps)
    if args.max_train_steps is None:
        args.max_train_steps = args.num_train_epochs * num_update_steps_per_epoch
    else:
        args.num_train_epochs = math.ceil(args.max_train_steps / num_update_steps_per_epoch)

    lr_scheduler = get_scheduler(
        name=args.lr_scheduler_type,
        optimizer=optimizer,
        num_warmup_steps=args.num_warmup_steps,
        num_training_steps=args.max_train_steps,
    )

    total_batch_size = args.batch_size * args.gradient_accumulation_steps

    logger.info("***** Running training *****")
    logger.info(f"  Num examples = {len(train_dataset)}")
    logger.info(f"  Num Epochs = {args.num_train_epochs}")
    logger.info(f"  Instantaneous batch size per device = {args.batch_size}")
    logger.info(f"  Gradient Accumulation steps = {args.gradient_accumulation_steps}")
    logger.info(f"  Total train batch size (w. parallel, distributed & accumulation) = {total_batch_size}")
    logger.info(f"  Total optimization steps = {args.max_train_steps}")

    # Only show the progress bar once on each machine.
    progress_bar = tqdm(range(args.max_train_steps))
    completed_steps = 0

    device = "cuda:0"
    model.to(device)
    best_loss = math.inf
    best_epoch = 0
    for epoch in range(args.initial_epoch, args.num_train_epochs):
        try:
            if (args.resume_path == None): model.train()
            else: model.train(resume_from_checkpoint=str(args.resume_path))
        except: model.train()

        for step, batch in enumerate(train_dataloader):
            batch = {k: v.to(device) for k, v in batch.items()}
            outputs = model(**batch)
            loss = outputs.loss
            loss = loss / args.gradient_accumulation_steps
            loss.backward()
            if step % args.gradient_accumulation_steps == 0 or step == len(train_dataloader) - 1:
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                lr_scheduler.step()
                optimizer.zero_grad()
                progress_bar.update(1)
                completed_steps += 1
            if completed_steps >= args.max_train_steps: break

        model.eval()
        losses = []

        for step, batch in enumerate(valid_dataloader):
            with torch.no_grad():
                batch = {k: v.to(device) for k, v in batch.items()}
                outputs = model(**batch)
            loss = outputs.loss
            losses.append(loss.item())
        losses = torch.tensor(losses)
        mloss = torch.mean(losses)

        if mloss < best_loss:
            best_loss = mloss
            best_epoch = epoch

        logger.info(f"epoch {epoch}: loss: {mloss}")
        wandb.log({"loss": mloss})
        output_dir = f"{args.directory}/checkpoint-{epoch}-{mloss:.5f}/"
        model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)

    best_model_dir = f"{args.directory}/checkpoint-{best_epoch}-{best_loss:.5f}/"
    model = GPT2LMHeadModel.from_pretrained(best_model_dir)
    model.to(device)
    model.eval()
    labes = []
    for step, batch in enumerate(valid_dataloader):
        for lab in batch["labels"]:
            labes.append(lab)
    compute_results = []
    eos_token = tokenizer.encode(['<eos_r>'])[0]
    for example in tqdm(labes):
        sindex = (example == tokenizer.encode("<sos_b>")[0])
        sindex = sindex.nonzero(as_tuple=True)[0].tolist()
        eindex = (example == eos_token)
        eindex = eindex.nonzero(as_tuple=True)[0].tolist()
        for start, end in zip(sindex, eindex):
            input_ids = example[:start]
            out = model.generate(input_ids=input_ids.reshape(1,-1).to(device),
                                 pad_token_id=tokenizer.eos_token_id,
                                 max_length=len(input_ids)+60,
                                 eos_token_id=eos_token)

            tpred = tokenizer.decode(out[0])
            ttrue = tokenizer.decode(example[:end+1])
            compute_results.append({"generated": tpred, "groundtruth": ttrue})
    with open(f"{args.directory}/examples-{best_epoch}-{best_loss:.5f}.json", "w") as fout: json.dump(compute_results, fout, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
