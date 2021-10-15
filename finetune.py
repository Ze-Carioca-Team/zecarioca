#!/usr/bin/env python
# coding=utf-8import json
import tqdm
import torch
from dialogparser import parser
from evaluate import compute
from torch.utils.data import Dataset, DataLoader
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from datasets import load_dataset, load_metric

checkpoint = "models/adrenaline_multiwoz/epoch56_trloss0.40_gpt2"
# checkpoint = "pierreguillou/gpt2-small-portuguese"

def add_tokens(examples):
    res = tokenizer(examples['text'], max_length=512, truncation=True,
                    padding='max_length')
    res['labels'] = res['input_ids'].copy()
    return res

def compute_metrics(pred):
    preds, labels = pred
    preds = parser(tokenizer.decode(preds))
    labels = parser(tokenizer.decode(labels))
    return compute(preds, labels)

def parse_args():
    parser = argparse.ArgumentParser(description="Finetune a transformers "
                                    "model on a causal language modeling task")
    parser.add_argument(
        "--checkpoint", type=str, default=None, help="A path for initial model."
    )
    parser.add_argument(
        "--train_file", type=str, default=None, help="A json file containing "
        "the training data."
    )
    parser.add_argument(
        "--validation_file", type=str, default=none, help="A json file "
        "containing the validation data."
    )
    return parser.parse_args()

def main():
    args = parse_args()

    with open("data/ontology.json") as fin:
        tokens = json.load(fin)

    tokenizer = GPT2Tokenizer.from_pretrained(args.checkpoint)
    model = GPT2LMHeadModel.from_pretrained(args.checkpoint)
    tokenizer.add_special_tokens({'additional_special_tokens': tokens})
    tokenizer.save_pretrained("models/tokenizer/")
    tokenizer.pad_token = tokenizer.eos_token
    model.resize_token_embeddings(len(tokenizer))
    datasets = load_dataset("json", data_files={"train":args.train_file,
                                                "valid":args.validation_file})
    tokenized = datasets.map(add_tokens, num_proc=4,
                             remove_columns=["id", "text"])


# training_args = TrainingArguments(
#     "test-clm",
#     evaluation_strategy="epoch",
#     per_device_train_batch_size=2,
#     gradient_accumulation_steps=32,
#     learning_rate=2e-5,
#     weight_decay=0.01,
#     num_train_epochs=100,
#     report_to="wandb",
#     run_name=checkpoint,
#     save_strategy="epoch",
# )

# trainer = Trainer(
#     model=model,
#     args=training_args,
#     train_dataset=tokenized["train"],
#     eval_dataset=tokenized["valid"],
#     compute_metrics=compute_metrics,
# )

# trainer.train()

# eval_results = trainer.evaluate()
# print(f"Perplexity: {torch.exp(eval_results['eval_loss']):.2f}")
