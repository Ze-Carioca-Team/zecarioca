import json
import nltk
from collections import defaultdict
from metrics import bleu

def compute(input_data, reference):
    reference_cat = defaultdict(list)
    for dialog in reference:
        for turn in dialog:
            sa = turn['action'].replace("][", "],[")
            for action in sa.split(","):
                reference_cat[action].append(turn['response'])
    return bleu(input_data, reference_cat)

def compute_bleu(input_data, reference):
    mean_bleu = 0.0
    for i in range(len(input_data)):
        mean_bleu += nltk.translate.bleu_score.sentence_bleu([reference[i]], input_data[i])
    mean_bleu = mean_bleu / float(len(input_data))
    return mean_bleu

if __name__ == "__main__":
    gen = []
    for line in open("data/process.train.json").readlines():
        gen.append(json.loads(line)['mwoz'])
    valid = []
    for line in open("data/process.valid.json").readlines():
        valid.append(json.loads(line)['mwoz'])
    for intent, score in compute(gen, valid).items():
        print(f"{intent:<15}: {score:.3f}")
