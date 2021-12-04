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
    print(intent, entity)
    dialog_domain = intent.split()[0]
    if dialog_domain in type_request:
        reqs = type_request[dialog_domain]
        if "cpf" in entity:
            query = reqs["query2"] if "placa" in entity else reqs["query"]
            for k, v in entity.items():
                query = query.replace(f"[{k}]", f"\'{v}\'")
            mydb = mysql.connector.connect(**db_data)
            mycursor = mydb.cursor()
            mycursor.execute(query)
            result = mycursor.fetchall()
            if len(result) > 1:
                action = action_string.format("[req_placa]")
                return action, []
            elif result:
                action = action_string.format("[info_valor][req_mais]")
                valor = random.choice(reqs["format"]).format(result[0][0])
                return action, [("[valor]", valor)]
            else:
                action = action_string.format("[invalido][req_cpf]")
                return action, []
        else:
            action = action_string.format("[req_cpf]")
            return action, []
    else:
        return "", []
