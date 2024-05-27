import telegram
from telegram.ext import Updater
import logging
from telegram.ext import CommandHandler, MessageHandler, BaseFilter, CallbackQueryHandler, JobQueue
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import pickle
import pprint
import os

if not telegram.__version__.startswith("13."):
    print("This bot only runs on 13.x version of the library. 13.15 reccomended.")
    exit()


script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)


# put the token in the same path inside a text file
with open("token.txt", "r") as f:
    TOKEN = f.read()


wait_dict = {}


def get_admin_ids(context, chat_id):
    return [admin.user.id for admin in context.bot.get_chat_administrators(chat_id)]


updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
j = updater.job_queue


def wait(update, context):
    global wait_dict
    a = 0
    tag = []
    fin = []
    mex = "Ecco gli altri 4 intrepidi giocatori:\n"
    for key in wait_dict:
        a += 1
        tag.append(list(key))
        print(tag, "1")
    if a == 4:
        context.bot.sendMessage(chat_id=update.message.chat_id,
                        text="Aspetta! Siete 5. Sto per taggare gli altri 4 player disponibili... Intanto puoi fare /startgame.")
        for i in tag:
            tempstr = str(i[0]) + "£" + str(i[1])
            fin.append(tempstr)
            print(fin, "2")
        for i in fin:
            c = i.split("£")
            context.bot.sendMessage(chat_id=c[1],
                            text="Hey! Ci sono altre 4 persone pronte a giocare su [Link alla chat](link alla chat). Fai presto, ti aspettano!")
            mex += "[" + str(c[0]) + "]" + "(tg://user?id=" + str(c[1]) + ")\n"
        context.bot.sendMessage(chat_id=update.message.chat_id, text=mex, parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        wait_dict[(update.message.from_user.first_name, update.message.from_user.id)] = j.run_once(delete,
                                                                                                   int(context.args[0]) * 60, (
                                                                                                   update.message.from_user.first_name,
                                                                                                   update.message.from_user.id))
        context.bot.sendMessage(chat_id=update.message.chat_id, text="Aggiunto in coda")


def test(update, context):
    context.bot.sendMessage(chat_id=update.message.chat_id, text="Toast!")


def delete(context, job):
    wait_dict.pop(job.context)
    context.bot.sendMessage(chat_id=-1001207423305, text="Rimosso dalla coda con successo")

def trywait(update, context):
    context.bot.sendMessage(chat_id=update.message.chat_id, text="Hey! Non c'è nessuno? Se usi il comando /wait ("
                                                                 "minuti, senza parentesi), puoi *metterti in coda* e quando arriverete a"
                                                                 " 5 player nell'arco di tempo indicato, il bot *vi avviserà cosìcché potrete giocare!*",
                            parse_mode=telegram.ParseMode.MARKDOWN)



dispatcher.add_handler(CommandHandler("wait", wait))
dispatcher.add_handler(CommandHandler("test", test))
dispatcher.add_handler(CommandHandler("trywait", trywait))

updater.start_polling()
