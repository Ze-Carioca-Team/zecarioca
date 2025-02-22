import re
import sys
import json
import torch
import logging
import argparse
import mysql.connector
from process.dialogparser import get_intents
# from connector import request_db
# from deanonymization import anonymization
from telegram import Update
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters, CallbackContext)
from transformers import GPT2Tokenizer, GPT2LMHeadModel

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

connection = {
    "host":"remotemysql.com",
    "user":"fcjRTVuTI0",
    "password":"rTnUuTKbvQ",
    "database":"fcjRTVuTI0",
}

def parse_args():
    parser = argparse.ArgumentParser(description="Finetune a transformers "
                                    "model on a causal language modeling task")
    parser.add_argument("--checkpoint", type=str, default=None,
        help="A path for initial model.")
    parser.add_argument("--dialog_domain", type=str, default="consulta_saldo",
        help="Domain of possible dialogs with chatbot.")
    return parser.parse_args()

def initialize_table():
    mydb = mysql.connector.connect(**connection)
    create_table_dialogs = "CREATE TABLE IF NOT EXISTS dialogs (id BIGINT NOT NULL AUTO_INCREMENT, dialog_domain VARCHAR(256) NOT NULL, situation BOOLEAN NOT NULL, PRIMARY KEY (id))"
    create_table_turns = "CREATE TABLE IF NOT EXISTS turns (turn_num INT NOT NULL, id_dialog BIGINT NOT NULL, speaker VARCHAR(256) NULL, utterance VARCHAR(2048) NOT NULL, utterance_delex VARCHAR(2048) NOT NULL, intent_action VARCHAR(256) NOT NULL, PRIMARY KEY (id_dialog, turn_num), FOREIGN KEY (id_dialog) REFERENCES dialogs(id))"
    mycursor = mydb.cursor()

    mycursor.execute(create_table_dialogs)
    mydb.commit()

    mycursor.execute(create_table_turns)
    mydb.commit()

    mydb.close()

def insert_dialog(dialog_domain):
    mydb = mysql.connector.connect(**connection)
    insert_query = "INSERT INTO dialogs (dialog_domain, situation) VALUES (%s, %s)"
    values = (dialog_domain, 0)
    mycursor = mydb.cursor()
    mycursor.execute(insert_query, values)
    mydb.commit()
    id_dialog = mycursor.lastrowid
    mydb.close()
    return id_dialog

def insert_turn(id_dialog, speaker, utterance,
                utterance_delex, intent_action, turn_num):
    mydb = mysql.connector.connect(**connection)
    insert_query = "INSERT INTO turns (id_dialog, turn_num, speaker, utterance, utterance_delex, intent_action) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (id_dialog, turn_num, speaker, utterance, utterance_delex, intent_action)
    mycursor = mydb.cursor()
    mycursor.execute(insert_query, values)
    mydb.commit()
    mydb.close()

def update_situation(id_dialog, situation):
    mydb = mysql.connector.connect(**connection)
    update_query = "UPDATE dialogs SET situation = "+str(situation)+" WHERE id = "+str(id_dialog)
    mycursor = mydb.cursor()
    mycursor.execute(update_query)
    mydb.commit()
    mydb.close()

def telegram_bot(args, debug_mode=False, deploy_mode='token-test'):
    with open('telegram.json') as fin: api = json.load(fin)
    tokenizer = GPT2Tokenizer.from_pretrained(args.checkpoint)
    model = GPT2LMHeadModel.from_pretrained(args.checkpoint)
    model.eval()

    updater = Updater(token=api[deploy_mode])
    dispatcher = updater.dispatcher
    # initialize_table()

    def start(update, context):
        response = ("Olá. Eu sou o Ze Carioca, como eu posso te ajudar? "
        "Ao final avalie a nossa conversa, utilizando a tag /correct "
        "quando eu me comporto adequadamente e /incorrect quando o meu "
        "comportamento saiu do esperado. O domínio da nossa conversa é "
        +args.dialog_domain+".")
        context.bot.send_message(chat_id=update.effective_chat.id, text=response)

    def restart(update, context):
        response = ("Olá. Eu sou o Ze Carioca, como eu posso te ajudar? "
        "Ao final avalie a nossa conversa, utilizando a tag /correct "
        "quando eu me comporto adequadamente e /incorrect quando o meu "
        "comportamento saiu do esperado. O domínio da nossa conversa é "
        +args.dialog_domain+".")
        context.bot.send_message(chat_id=update.effective_chat.id, text=response)
        if 'id' in context.user_data: context.user_data.pop('id')
        if 'variables' in context.user_data: context.user_data.pop('variables')
        if 'turn' in context.user_data: context.user_data.pop('turn')
        if 'msg' in context.user_data: context.user_data.pop('msg')

    def correct(update, context):
        if 'id' in context.user_data: update_situation(context.user_data['id'], 1)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Diálogo correto adicionado com sucesso! Obrigada!")

    def incorrect(update, context):
        if 'id' in context.user_data: update_situation(context.user_data['id'], 0)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Diálogo incorreto adicionado com sucesso! Obrigada!")

    def reply(update, context):
        if 'msg' not in context.user_data: context.user_data['msg'] = ""

        msg = '<sos_u>'+update.message.text.lower()+'<eos_u><sos_b>'
        logging.info("[USER] " + context.user_data['msg'])
        contextmsg = tokenizer.encode(context.user_data['msg']+msg)
        context_length = len(contextmsg)
        max_len=80

        outputs = model.generate(input_ids=torch.LongTensor(
            contextmsg).reshape(1,-1),
            max_length=context_length+max_len,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.encode(['<eos_b>'])[0])
        generated = outputs[0].numpy().tolist()
        decoded_output = tokenizer.decode(generated)

        # action_db, trans = request_db(decoded_output.split('<eos_u>')[-1])
        action_db = ""
        # logging.info("[DATABASE] " + action_db + str(trans))
        action_db = tokenizer.encode(action_db)
        outputs = model.generate(input_ids=torch.LongTensor(
            generated+action_db).reshape(1,-1),
            max_length=context_length+max_len,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.encode(['<eos_r>'])[0])
        generated = outputs[0].numpy().tolist()

        decoded_output = tokenizer.decode(generated)
        context.user_data['msg'] = decoded_output
        # for k,v in trans:
        #     decoded_output = decoded_output.replace(k,v,1)

        system_response = decoded_output.split('<sos_r>')[-1].split('<eos_r>')[0]

        logging.info("[SYSTEM] "+decoded_output)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=system_response)
        if debug_mode:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=decoded_output)

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    restart_handler = CommandHandler('restart', restart)
    dispatcher.add_handler(restart_handler)
    #correct_handler = CommandHandler('correct', correct)
    #dispatcher.add_handler(correct_handler)
    #incorrect_handler = CommandHandler('incorrect', incorrect)
    #dispatcher.add_handler(incorrect_handler)
    reply_handler = MessageHandler(Filters.text & (~Filters.command), reply)
    dispatcher.add_handler(reply_handler)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    args = parse_args()
    telegram_bot(args, debug_mode=True)
