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

    :input_data: TODO
    :reference_dialogs: TODO
    :returns: TODO

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
