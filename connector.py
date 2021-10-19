#!/usr/bin/env python
# coding: utf-8

import os, json
contents = []
with open('./data/process.train.json', 'r') as fp:
    d = fp.readline()
    while d:
        contents.append(json.loads(d))
        d = fp.readline()

def parse_data(d):
    ret = []
    d = d.replace("><", "> <").replace("][", '] [').split(" ")
    d = [a for a in d if len(a)>0]

    start = '<sos_b>'
    stop  = '<eos_b>'
    founds = []
    is_adding = False
    for i in range(len(d)):
        if d[i]==stop:
            is_adding = False
        if is_adding:
            founds.append(d[i])
        if d[i]==start:
            is_adding = True

    if '[consulta_saldo]' in founds or True:
        if 'cpf' in founds and 'placa' in founds:
            cpf_index = founds.index('cpf')+1
            placa_index = founds.index('placa')+1

            cpf = ""
            placa = ""
            while True:
                if founds[cpf_index][0]=='[' or founds[cpf_index] in ['[', 'nome', 'cpf', 'email', 'placa']:
                    break
                cpf += founds[cpf_index]
                cpf_index += 1
                if len(cpf)>11:
                    break

            while True:
                if founds[placa_index][0]=='[' or founds[placa_index] in ['[', 'nome', 'cpf', 'email', 'placa']:
                    break
                placa += founds[placa_index]
                placa_index += 1
                if len(placa)>7:
                    break

            cpf = cpf.replace(".", "").replace("-", "")
            placa = placa.replace("-", "")


            if len(placa)==7 and len(cpf)==11:
                ret.append({'type': 'saldo', 'fields':{'cpf': cpf, 'placa': placa}})

        return ret

import mysql.connector

mydb = mysql.connector.connect(
  host="remotemysql.com",
  user="fcjRTVuTI0",
  password="rTnUuTKbvQ",
  database="fcjRTVuTI0"
)

def request_db(d, mycursor):
    ret = []
    for tipo in d:

        if tipo['type']=='saldo':
            if not 'cpf' in tipo['fields'] or not 'placa' in tipo['fields']:
                raise Exception("Missing parameter CPF of PLACA for request SALDO")

            sql = f"SELECT balance FROM clients c WHERE cpf='{tipo['fields']['cpf']}' AND c.id IN(SELECT clients_id FROM vehicles WHERE plate='{tipo['fields']['placa']}') "
            print(sql)
            mycursor.execute(sql)
            myresult = mycursor.fetchall()
            try:
                ret.append(myresult[0][0])
            except Exception as e:
                print(e)
                ret.append("CPF and PLACA not found on database")

    return ret
