import sys
import json
import torch
import logging
import argparse
import mysql.connector
from connector import parse_data, request_db
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

def parse_args():
    parser = argparse.ArgumentParser(description="Finetune a transformers "
                                    "model on a causal language modeling task")
    parser.add_argument("--checkpoint", type=str, default=None,
        help="A path for initial model.")
    return parser.parse_args()

def telegram_bot(args):
    mydb = mysql.connector.connect(
      host="remotemysql.com",
      user="fcjRTVuTI0",
      password="rTnUuTKbvQ",
      database="fcjRTVuTI0"
    )
    with open('telegram.json') as fin:
        api = json.load(fin)
    with torch.no_grad():
        tokenizer = GPT2Tokenizer.from_pretrained(args.checkpoint)
        model = GPT2LMHeadModel.from_pretrained(args.checkpoint)

        updater = Updater(token=api['token'])
        dispatcher = updater.dispatcher

        def start(update, context):
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Hi. I am a Ze Carioca, how can I help you?")

        def restart(update, context):
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Hi. I am a Ze Carioca, how can I help you?")
            context.user_data['msg'] = []

        def reply(update, context):
            msg = '<sos_u>'+update.message.text.lower()+'<eos_u>'
            msg = tokenizer.encode(msg, add_special_tokens=True)
            if 'msg' not in context.user_data:
                context.user_data['msg'] = []
            context.user_data['msg'] += msg

            logging.info("[USER] "+tokenizer.decode(context.user_data['msg']))
            context_length = len(context.user_data['msg'])
            max_len=60

            outputs = model.generate(input_ids=torch.LongTensor(
                context.user_data['msg']).reshape(1,-1),
                max_length=context_length+max_len, temperature=0.7,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.encode(['<eos_r>'])[0])

            generated = outputs[0].cpu().numpy().tolist()
            generated = generated[context_length:]

            context.user_data['msg'] += generated
            decoded_output = tokenizer.decode(generated)
            parsed = parse_data(decoded_output)
            print("="*80)
            print(decoded_output)
            print(parse_data(decoded_output))
            logging.info("[SYSTEM] "+decoded_output)
            decoded_output = decoded_output.split('<sos_r>')[-1]\
                .rstrip('<eos_r>')
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=decoded_output)

        start_handler = CommandHandler('start', start)
        dispatcher.add_handler(start_handler)
        restart_handler = CommandHandler('restart', restart)
        dispatcher.add_handler(restart_handler)
        reply_handler = MessageHandler(Filters.text & (~Filters.command), reply)
        dispatcher.add_handler(reply_handler)

        updater.start_polling()
        updater.idle()

if __name__ == "__main__":
    args = parse_args()
    telegram_bot(args)
