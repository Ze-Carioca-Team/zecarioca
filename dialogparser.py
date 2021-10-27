def parser(genstring):
    """TODO: Docstring for parser.

    :genstring: TODO
    :returns: TODO

    """
    dialog = []
    turn = genstring.split(" <eos_u>")[-1]
    try:
        curr, tail = tail.split(" <eos_b>")
        bs = curr.lstrip("<sos_b> ")
        curr, tail = tail.split(" <eos_a>")
        sa = curr.lstrip("<sos_a> ")
        resp = tail.lstrip("<sos_r> ")
        return {
            "belief": bs,
            "action": sa,
            "response": resp,
        }
    except Exception as e:
        return {
            "belief": "a",
            "action": "a",
            "response": "a",
         }