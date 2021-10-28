from collections import defaultdict
from sacrebleu import corpus_bleu

def richness(input_data):
    """TODO: Docstring for richness.

    :input_data: TODO
    :returns: TODO

    """
    pass

def success(input_data, db, goals, booked_domains):
    """TODO: Docstring for success.

    :input_data: TODO
    :db: TODO
    :goals: TODO
    :booked_domains: TODO
    :returns: TODO

    """
    pass

def bleu(input_data, reference_dialogs):
    """TODO: Docstring for bleu.

    :input_data: List with a dict containing belief state, action, and
    response.
    :reference: Expected states for the input_data.
    :returns: Dict with computed bleu for every action.

    """
    hyps = [dialog["response"] for dialog in input_data]
    return {r : corpus_bleu(hyps, reference_dialogs[r]).score for r in\
            reference_dialogs}

def jointacc(input_data, reference_states, fuzzy_ratio=95):
    """TODO: Docstring for jointacc.

    :input_data: TODO
    :reference_states: TODO
    :fuzzy_ratio: TODO
    :returns: TODO

    """
    pass

def compute(input_data, reference):
    """TODO: Docstring for compute.

    :input_data: List with a dict containing belief state, action, and
    response.
    :reference: Expected states for the input_data.
    :returns: Dict with all computed metrics.

    """
    reference_cat = defaultdict(list)
    for dialog in reference:
        for action in dialog['action'].split(" "):
            reference_cat[action].append(dialog['response'])
    return {"BLEU": bleu(input_data, reference_cat)}
