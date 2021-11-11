#!/usr/bin/env python
# coding: utf-8
import json
import random
from dialogparser import get_belief
import mysql.connector

db_data = {
    'host': "remotemysql.com",
    'user': "fcjRTVuTI0",
    'password': "rTnUuTKbvQ",
    'database': "fcjRTVuTI0"
}

action_string = "<sos_a>{}<eos_a>"

with open('type_request.json') as filer:
    type_request = json.load(filer)

def request_db(belief):
    intent, entity = get_belief(belief)
    dialog_domain = intent.split()[0]
    if dialog_domain in type_request:
        reqs = type_request[dialog_domain]
        parameters = {p:p in entity.keys() for p in reqs["parameters"]}
        if all(parameters.values()):
            query = reqs["query"]
            for k, v in entity.items():
                query = query.replace(f"[{k}]", f"\'{v}\'")
            mydb = mysql.connector.connect(**db_data)
            mycursor = mydb.cursor()
            mycursor.execute(query)
            result = mycursor.fetchall()
            if result:
                action = action_string.format("[info_valor]")
                valor = random.choice(reqs["format"]).format(result[0][0])
                return action, [("[valor]", valor)]
            else:
                action = action_string.format("[invalido]")
                return action, []
        else:
            action = "".join([f"[req_{k}]" for (k,v) in parameters.items() if not v])
            action = action_string.format(action)
            return action, []
    else:
        return "", []
