import json
import glob

for fname in glob.glob("data/MultiWOZ_2.2/**/*"):
    with open(fname) as data:
        jsondata = json.load(data)
    for dialog in jsondata:
        services = dialog["services"]
        if "restaurant" not in services:
            continue
        for turn in dialog["turns"]:
            if int(turn["turn_id"]) % 2 == 0:
                print("User:",turn["utterance"])
                for frame in turn["frames"]:
                    if frame["service"] in services and frame["state"]["active_intent"] != "NONE":
                        print("Intent:", frame["state"]["active_intent"].replace("_", " "))
                        print("Requested:", end=" ")
                        for value in frame["state"]["requested_slots"]:
                            print(value.replace("-"," "), end=" ")
                        print(" ")
                        print("Belief:", end=" ")
                        for value in frame["state"]["slot_values"]:
                            print(value.replace("-"," "), " ".join(frame["state"]["slot_values"][value]), end=" ")
                        print()

            else:
                print("System:", turn["utterance"])
                print()
        print("####")
        exit()
