#!/usr/bin/env python
# coding=utf-8
import json
import math
import wandb
import logging
import argparse
from tqdm import tqdm
from process.dialogparser import parser
from analysis.metrics import compute_all

def parse_args():
    parser = argparse.ArgumentParser(description="Finetune a transformers "
                                    "model on a causal language modeling task")
    parser.add_argument("--file", type=str, help="A path to save model.")
    return parser.parse_args()

def main():
    args = parse_args()
    with open(args.file) as fin:
        data = json.load(fin)

    preds = [parser(v["generated"]) for v in data]
    trues = [parser(v["groundtruth"]) for v in data]
    print(compute_all(preds, trues))


if __name__ == "__main__":
    main()
