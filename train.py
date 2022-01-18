import os
import math
import tqdm
import glob
import pandas as pd
import torch
from itertools import chain
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from transformers import Trainer, TrainingArguments
from datasets import load_dataset, load_metric

files = "clear_threads/*.parquet"
checkpoint = "models/pratofeito"
block_size = 128

tokenizer = GPT2Tokenizer.from_pretrained(checkpoint)
model = GPT2LMHeadModel.from_pretrained(checkpoint)

train_files, validation_files = train_test_split(glob.glob(files),
                                                 test_size=0.1)

datasets = load_dataset("parquet", data_files={"train": train_files,
                                               "validation": validation_files})
datasets = datasets.filter(
    lambda x: x['text'] is not None and x['reply'] is not None)
datasets = datasets.filter(
    lambda x: len(x['text']) > 3 and len(x['reply']) > 3\
    and len(x['text']+x['reply']) < 240)
datasets = datasets.filter(
    lambda x: x['text'].endswith((".", "?", "!")) and\
    x['reply'].endswith((".", "?", "!")))

special_tokens = ["<sos_u>", "<eos_u>",
                  "<sos_b>", "<eos_b>",
                  "<sos_r>", "<eos_r>"]
tokenizer.add_special_tokens({'additional_special_tokens': special_tokens})
model.resize_token_embeddings(len(tokenizer))

def prefix_function(examples):
    examples["text"] =  "<sos_u> "+examples["text"]+" <eos_u>"
    examples["topic"] = "<sos_b> "+examples["topic"]+" <eos_b>"
    examples["reply"] = "<sos_r> "+examples["reply"]+" <eos_r>"
    examples["encoded"] = examples["text"]+examples["topic"]+examples["reply"]
    return examples

column_names = datasets["train"].column_names

datasets = datasets.map(
    prefix_function,
    remove_columns=column_names,
)

def tokenizer_function(examples):
    return tokenizer(examples["encoded"], truncation=True, padding="max_length",
                     max_length=block_size)

column_names = datasets["train"].column_names

datasets = datasets.map(
    tokenizer_function,
    batched=True,
    num_proc=4,
    remove_columns=column_names,
)

column_names = datasets["train"].column_names
print(column_names)

def group_texts(examples):
    concatenated_examples = {k: list(chain(*examples[k])) for k in examples.keys()}
    total_length = len(concatenated_examples[list(examples.keys())[0]])
    if total_length >= block_size:
        total_length = (total_length // block_size) * block_size
    result = {
        k: [t[i : i + block_size] for i in range(0, total_length, block_size)]
        for k, t in concatenated_examples.items()
    }
    result["labels"] = result["input_ids"].copy()
    return result

lm_datasets = datasets.map(
    group_texts,
    batched=True,
    num_proc=4,
)

training_args = TrainingArguments(
    "models/forums-clm",
    run_name="forums-clm",
    evaluation_strategy="epoch",
    per_device_train_batch_size=8,
    learning_rate=2e-5,
    weight_decay=0.01,
    warmup_steps=2000,
    num_train_epochs=20,
    report_to="wandb",
    save_strategy="epoch"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=lm_datasets["train"],
    eval_dataset=lm_datasets["validation"],
)

trainer.train()

eval_results = trainer.evaluate()
print(f"Perplexity: {math.exp(eval_results['eval_loss']):.2f}")
