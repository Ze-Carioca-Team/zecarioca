import os
import json
import glob
import tqdm
import random
import pandas as pd


path = "clear_threads/"
files = glob.glob(path+"*_*.tsv")
ids = json.load(open("category_ids.json"))
names = json.load(open("categories.json"))

frames = []
counter = 0
fsize = len(files)

for filein in tqdm.tqdm(files):
    tid = filein.split('/')[-1].split('_')[0]
    counter += 1
    df = pd.read_csv(filein, delimiter='\t', quoting=3, header=None,
                     names=["timestamp", "id", "text"])
    df.drop(columns=['timestamp'], inplace=True)
    df['reply'] = df['text'].shift(-1)
    df = df.iloc[:-1]
    namethr, namesub = ids[tid]
    if namethr == "36":
        continue
    df['topic'] = names[namethr]["name"].lower()+" "+names[namethr]["subs"][namesub].lower()
    try:
        df.drop(df[(df.text.str.len() < 3) | (df.reply.str.len() < 3)].index,
                inplace=True)
    except:
        print("Can't process", filein)
    os.remove(filein)
    frames.append(df)
    if counter % 1000 == 0 or counter == fsize:
        out = pd.concat(frames, axis=0, ignore_index=True)
        out.dropna(axis=0, inplace=True)
        frames = []
        out.to_parquet(path+str(counter)+'.parquet')
        del out
