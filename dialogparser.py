def parser(genstring):
    """TODO: Docstring for parser.

    :genstring: TODO
    :returns: TODO

    """
    dialog = []
    for num, turn in enumerate(genstring.split(" <eos_r>")):
        if not turn: continue
        curr, tail = turn.split(" <eos_u>")
        utt = curr.lstrip("<sos_u> ")
        curr, tail = tail.split(" <eos_b>")
        bs = curr.lstrip("<sos_b> ")
        curr, tail = tail.split(" <eos_a>")
        sa = curr.lstrip("<sos_a> ")
        resp = tail.lstrip("<sos_r> ")
        dialog.append({
            "utterance": utt,
            "belief": bs,
            "action": sa,
            "response": resp,
            "turn-num": num
        })
    return dialog

