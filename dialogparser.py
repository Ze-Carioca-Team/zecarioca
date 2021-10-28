import re

def get_intents(sentence):
    result = "".join(re.compile(r'\[\S+\]').findall(sentence))
    return result

def remove_tags(sentence):
    result = re.sub(r'\[\S+\]', "", sentence)
    result = re.sub(r'\<\S+\>', "", result)
    return result

def parser(genstring):
    """TODO: Docstring for parser.

    :genstring: TODO
    :returns: TODO

    """
    dialog = []
    for num, turn in enumerate(genstring.split(" <eos_r>")):
        if not turn: continue
        try:
            utt = turn.split('<sos_u>')[-1].split('<eos_u>')[0]
            bs = get_intents(turn.split('<sos_b>')[-1].split('<eos_b>')[0])
            sa = get_intents(turn.split('<sos_a>')[-1].split('<eos_a>')[0])
            resp = turn.split('<sos_r>')[-1].split('<eos_r>')[0]
            dialog.append({
                "utterance": utt,
                "belief": bs,
                "action": sa,
                "response": resp,
                "turn-num": num
            })
        except:
            print("String can't be parsed")
            dialog.append({
                "utterance": "a",
                "belief": "a",
                "action": "a",
                "response": "a",
                "turn-num": "a"
            })
    return dialog
