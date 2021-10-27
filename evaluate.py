import json
from collections import defaultdict
from metrics import bleu



def compute(input_data, reference):
    reference_cat = defaultdict(list)
    for dialog in reference:
        for action in dialog['action'].split(" "):
            reference_cat[action].append(dialog['response'])
    return bleu(input_data, reference_cat)
