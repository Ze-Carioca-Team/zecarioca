#!/usr/bin/env python
# coding: utf-8
import json
import random

db_data = {
    'host': "remotemysql.com",
    'user': "fcjRTVuTI0",
    'password': "rTnUuTKbvQ",
    'database': "fcjRTVuTI0"
}
with open('type_request.json') as filer:
    type_request = json.load(filer)

def request_db (dialog_domain, sentence, variables):
    response = sentence
    if (dialog_domain in type_request.keys()):
        for typer in type_request[dialog_domain]:
            for value in typer["result"]:
                if (value in response):
                    query = typer["query"]
                    for param in typer["parameters"]:
                        if (param[0] in variables.keys()):
                            if (param[1] == 1):
                                query = query.replace("["+param[0]+"]", "'"+variables[param[0]]+"'")
                            else: query = query.replace("["+param[0]+"]", variables[param[0]])
                        else:
                            default_sample = random.sample(typer["default"], k = 1)[0]
                            return False, default_sample[0], default_sample[1]

                    mydb = mysql.connector.connect(host=db_data['host'], user=db_data['user'],
                                                   password=db_data['password'], database=db_data['database'])
                    mycursor = mydb.cursor()
                    mycursor.execute(query)
                    try:
                        result = mycursor.fetchall()[0][0]
                        rformat = random.sample(typer["format"], k = 1)[0]
                        response = response.replace(value, rformat.replace("[???]", str(result)))
                        return True, response, ""
                    except:
                        default_sample = random.sample(typer["default"], k = 1)[0]
                        return False, default_sample[0], default_sample[1]
    else: return True, response, ""
    return True, response, ""