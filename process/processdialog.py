import json
import tqdm
import random
import argparse
from dialogparser import parser
from transformers import GPT2Tokenizer, GPT2LMHeadModel

random.seed(42)

def parse_args():
    parser = argparse.ArgumentParser(description="Finetune a transformers "
                                    "model on a causal language modeling task")
    parser.add_argument("--file", type=str, default=None, help="A path for the file.")
    return parser.parse_args()

def main():
    args = parse_args()
    with open(args.file) as fin:
        data = json.load(fin)
        tokens = data['ontology']['intents'] + data['ontology']['actions'] + ["<sos_u>", "<sos_b>", "<sos_a>", "<sos_r>", "<eos_u>", "<eos_b>", "<eos_a>", "<eos_r>"]
        dialogues = []
        for d in tqdm.tqdm(data['dialogs']):
            dialog = ''
            for turn in range(len(d['turns'])//2):
                t = d['turns'][turn*2:turn*2+2]
                utterance = f"<sos_u> {t[0]['utterance'].lower()} <eos_u>"
                intents = []
                for slot in t[0]['slot-values']:
                    if isinstance(t[0]['slot-values'][slot], list):
                        parse = [[slot, v] for v in t[0]['slot-values'][slot]]
                        intents += [item for sublist in parse for item in sublist]
                    else:
                        intents += [slot, t[0]['slot-values'][slot]]
                try:
                    bs = [t[0]['intent']] + intents
                    belief = "<sos_b> " + t[0].get('domain','') + " ".join(bs).lower() + " <eos_b>"
                    action = "<sos_a> " + t[1]['action'] + " <eos_a>"
                except:
                    print(t)
                    exit()
                response = f"<sos_r> {t[1]['utterance_delex']} <eos_r>"
                dialog += utterance+belief+action+response
            dialogues.append({'id':d['id'], 'text':dialog})
        random.shuffle(dialogues)
        fname = args.file.replace('out.dialogs', 'process')
        with open("data/ontology.json", "w") as fonto:
            json.dump(tokens, fonto)
        with open(fname, "w") as fdata:
            for i, line in enumerate(dialogues):
                print(json.dumps(line), file=fdata)

if __name__ == "__main__":
    main()
