from collections import defaultdict
from pprint import pprint
import json
from pathlib import Path
from click import progressbar
from tqdm import tqdm

path = Path("data/multiwoz/")
with (path/"dialog_acts.json").open() as fin:
    acts = json.load(fin)
counter = defaultdict(int)
examples = defaultdict(list)
progressbar = tqdm(list(path.glob("**/dialogues_*")))

for split in ["train", "test", "dev"]:
    out_json = {}
    for fname in path.glob(split+"/dialogues_*"):
        progressbar.update(1)
        with fname.open() as data:
            jsondata = json.load(data)
        for dialog in jsondata:
            encoded_string = ""
            services = dialog["services"]
            for turn in dialog["turns"]:
                if int(turn["turn_id"]) % 2 == 0:
                    encoded_string += "<sos_u> " + turn["utterance"] + " <eos_u>"
                    encoded_string += " <sos_b> "
                    for frame in turn["frames"]:
                        if frame["service"] in services and frame["state"]["active_intent"] != "NONE":
                            encoded_string += "["+frame["state"]["active_intent"]+"] "
                            for value in frame["state"]["requested_slots"]:
                                encoded_string += value + " "
                            for value in frame["state"]["slot_values"]:
                                encoded_string += value + " " + " ".join(frame["state"]["slot_values"][value]) + " "
                    encoded_string += "<eos_b> "
                else:
                    dialog_acts = acts[dialog["dialogue_id"]][turn["turn_id"]]
                    act_string = []
                    response = turn["utterance"]
                    for key in dialog_acts["dialog_act"]:
                        act_string.append("["+key.lower()+"]")
                        for param in dialog_acts["dialog_act"][key]:
                            if param[0] != "none":
                                act_string.append(" ".join(param))
                                if param[1] != "?":
                                    if param[1] in response:
                                        response = response.replace(param[1], f"<value_{param[0]}>")
                                    else:
                                        print(fname, dialog["dialogue_id"])
                                        print(response)
                                        print(param)
                                        counter[param[1]] += 1
                                        examples[param[1]].append(response)
                    encoded_string += "<sos_a> " + " ".join(act_string) + " <eos_a> "
                    encoded_string += "<sos_r>" + response + "<eos_r>"
            out_json[dialog["dialogue_id"]] = encoded_string
    with (path/f"{split}/encoded.json").open("w") as fout:
        json.dump(out_json, fout, indent=4)

for key in sorted(counter.items(), key=lambda x: x[1])[:-1]:
    print(key)
    #pprint(examples[key[0]], indent=4)