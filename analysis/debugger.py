#!/usr/bin/env python
# coding=utf-8
import sys
import torch
import argparse
from transformers import GPT2Tokenizer, GPT2LMHeadModel

def parse_args():
    parser = argparse.ArgumentParser(description="Debugger for the chatbot dialogue")
    parser.add_argument("--checkpoint", type=str,
        default="models/adrenaline_multiwoz/epoch56_trloss0.40_gpt2",
        help="A path for initial model.")
    return parser.parse_args()

def main():
    args = parse_args()
    tokenizer = GPT2Tokenizer.from_pretrained(args.checkpoint)
    model = GPT2LMHeadModel.from_pretrained(args.checkpoint)
    text = ""
    eos_token = tokenizer.encode(['<eos_r>'])[0]
    for line in sys.stdin:
        input_ids = tokenizer.encode(text + "<sos_u>"+line+"<eos_u>")
        out = model.generate(input_ids=torch.LongTensor(input_ids).reshape(1,-1),
                             pad_token_id=tokenizer.eos_token_id,
                             max_length=len(input_ids)+60,
                             eos_token_id=eos_token)
        out = (tokenizer.decode(out[0]))
        text += out
        print(out)


if __name__ == "__main__":
    main()
