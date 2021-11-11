import re

def get_belief(sentence):
    intent = " ".join(re.compile(r'\[\S+\]').findall(sentence))
    entity = [w for w in sentence.split() if not w.startswith(('<', '['))]
    entity = dict(zip(entity[0::2], entity[1::2]))
    return intent, entity

def get_intents(sentence):
    result = " ".join(re.compile(r'\[\S+\]').findall(sentence))
    return result

def remove_tags(sentence):
    result = re.sub(r'\[\S+\]', "", sentence)
    result = " ".join(re.sub(r'\<\S+\>', "", result).split())
    return result

def parser(genstring):
    """TODO: Docstring for parser.

    :genstring: TODO
    :returns: TODO

    """
    turn = genstring.split("<eos_u>")[-1]
    try:
        bs = turn.split('<sos_b>')[-1].split('<eos_b>')[0]
        sa = get_intents(turn.split('<sos_a>')[-1].split('<eos_a>')[0])
        resp = turn.split('<sos_r>')[-1].split('<eos_r>')[0]
        return {
            "belief": bs,
            "action": sa,
            "response": resp
        }
    except:
        print("String can't be parsed")
        return {
            "belief": "a",
            "action": "a",
            "response": "a"
        }
    return dialog
