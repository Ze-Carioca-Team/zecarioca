import math
from process.dialogparser import get_intents, remove_tags
from collections import defaultdict, Counter
from lexical_diversity import lex_div as ld
from sacrebleu import corpus_bleu
from thefuzz import fuzz

def richness(input_data):
    """TODO: Docstring for richness.

    :input_data: List with a dict containing belief state, action, and
    response.
    :returns: TODO

    """
    avg_lens, msttr, count = 0, 0, 0
    unique_grams = [Counter() for _ in range(3)]
    all_tokens = []

    for turn in input_data:
        tokens = ld.tokenize(turn["response"])
        all_tokens.extend(tokens)

        avg_lens  += len(tokens)
        count += 1

        unique_grams[0].update(tokens)
        unique_grams[1].update([(a, b) for a, b in zip(tokens, tokens[1:])])
        unique_grams[2].update([(a, b, c) for a, b, c in zip(tokens, tokens[1:], tokens[2:])])

    avg_lens  /= count
    msttr = ld.msttr(all_tokens, window_length=50)
    unique_grams_count = [len(c) for c in unique_grams]

    total = sum(v for v in unique_grams[0].values())
    probs = [(u/total) for u in unique_grams[0].values()]
    entropy = -sum(p * math.log(p, 2) for p in probs)

    cond = [unique_grams[1][(h, w)]/unique_grams[0][h] for h, w in unique_grams[1]]
    join = [unique_grams[1][(h, w)]/total for h, w in unique_grams[1]]
    cond_entropy = -sum(j * math.log(c, 2) for c, j in zip(cond, join))

    return {
        'entropy'         : entropy,
        'cond_entropy'    : cond_entropy,
        'avg_lengths'     : avg_lens,
        'msttr'           : msttr,
        'num_unigrams'    : unique_grams_count[0],
        'num_bigrams'     : unique_grams_count[1],
        'num_trigrams'    : unique_grams_count[2]
    }

def success(pred_data, true_data):
    """TODO: Docstring for success.

    :input_data: TODO
    :input_data: List with a dict containing belief state, action, and
    response.
    :db: TODO
    :goals: TODO
    :booked_domains: TODO
    :returns: TODO

    """
    jaccard = {"belief":[], "action":[]}
    for pred, true in zip(pred_data, true_data):
        for intent in jaccard.keys():
            paction = set(get_intents(pred[intent]).split())
            taction = set(get_intents(true[intent]).split())
            union = paction | taction
            intersection = paction & taction
            jaccard[intent].append(len(intersection)/len(union))
    return {
        "belief": sum(jaccard["belief"])/len(jaccard["belief"]),
        "action": sum(jaccard["action"])/len(jaccard["action"]),
    }

def bleu(input_data, true_data):
    """TODO: Docstring for bleu.

    :input_data: List with a dict containing belief state, action, and
    response.
    :reference: Expected states for the input_data.
    :returns: Dict with computed bleu for every action.

    """
    hyps = [dialog["response"] for dialog in input_data]
    true = [dialog["response"] for dialog in true_data]
    return corpus_bleu(hyps, true).score

def ibleu(input_data, reference_dialogs):
    """TODO: Docstring for ibleu.

    :input_data: List with a dict containing belief state, action, and
    response.
    :reference: Expected states for the input_data.
    :returns: Dict with computed bleu for every action.

    """
    hyps = [dialog["response"] for dialog in input_data]
    return {r : corpus_bleu(hyps, reference_dialogs[r]).score for r in\
            reference_dialogs}

def inform(input_data, reference_states, fuzzy_ratio=95):
    """TODO: Docstring for jointacc.

    :input_data: TODO
    :reference_states: TODO
    :fuzzy_ratio: TODO
    :returns: TODO

    """
    scores = []
    pbelief = [remove_tags(dialog["belief"]) for dialog in input_data]
    tbelief = [remove_tags(dialog["belief"]) for dialog in reference_states]
    for p, t in zip(pbelief, tbelief):
        scores.append(fuzz.ratio(p, t)/100)
    return sum(scores)/len(scores)

def compute_all(pred_data, true_data):
    """TODO: Docstring for compute.

    :input_data: List with a dict containing belief state, action, and
    response.
    :reference: Expected states for the input_data.
    :returns: Dict with all computed metrics.

    """
    reference_cat = defaultdict(list)
    for dialog in true_data:
        for action in dialog['action'].split(" "):
            reference_cat[action].append(dialog['response'])
    return {
        "BLEU": bleu(pred_data, true_data),
        "iBLEU": ibleu(pred_data, reference_cat),
        "RICHNESS": richness(pred_data),
        "INFORM": inform(pred_data, true_data),
        "SUCCESS": success(pred_data, true_data),
    }
