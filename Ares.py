import telegram
from telegram.ext import Updater
import logging
from telegram.ext import CommandHandler, MessageHandler, BaseFilter, CallbackQueryHandler, PicklePersistence
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import pprint
import json
import os

if not telegram.__version__.startswith("13."):
    print("This bot only runs on 13.x version of the library. 13.15 reccomended.")
    exit()


script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)


# put the token in the same path inside a text file
with open("token.txt", "r") as f:
    TOKEN = f.read()


my_persistence = PicklePersistence(filename='Persistence.pickle')
immuni = {}
are_immuni = False


def get_admin_ids(context, chat_id):
    return [admin.user.id for admin in context.bot.get_chat_administrators(chat_id)]


updater = Updater(token=TOKEN, use_context=True, persistence=my_persistence)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def bong(update, context):
    context.bot.sendMessage(chat_id=update.message.chat_id, text="BONG BONG BONG BONG")


def newrolelist(update, context):
    if update.message.from_user.id in get_admin_ids(context, update.message.chat_id):
        context.chat_data["stringa_finale"] = ""
        try:
            entities = update.message.reply_to_message.entities
            context.chat_data["role_list"] = {}
            context.chat_data["numero"] = 0
            if "are_immuni" in context.chat_data:
                if context.chat_data["are_immuni"]:
                    context.chat_data["stringa_finale"] = "*Lista immuni*:\n"
                    for id, nome in context.chat_data["immuni"].items():
                        context.chat_data["stringa_finale"] += "[" + nome + "](tg://user?id=" + str(id) + ")\n"
                context.chat_data["stringa_finale"] += "\n*Lista dei giocatori:*\n"
                context.chat_data["temp_dict"] = {}
                for i in entities:
                    if i.type == "text_mention":
                        context.chat_data["numero"] += 1
                        context.chat_data["stringa_finale"] += str(context.chat_data["numero"]) + ". " + "[" + i["user"]["first_name"] + "](tg://user?id=" + str(
                            i["user"]["id"]) + "): " + "\n"
                        context.chat_data["role_list"][(i["user"]["first_name"], i["user"]["id"])] = ""
                context.chat_data["stringa_finale"] += "\nLista creata!\nNumero giocatori: *" + str(context.chat_data["numero"]) + "*"
                context.bot.sendMessage(chat_id=update.message.chat_id, text=context.chat_data["stringa_finale"], parse_mode=telegram.ParseMode.MARKDOWN)
            else:
                context.chat_data["are_immuni"] = False
                newrolelist(update, context)
        except AttributeError:
            update.message.reply_text("Rispondi a un messaggio del bot.")


def upd(update, context):
    if update.message.from_user.id in get_admin_ids(context, update.message.chat_id):
        entities = update.message.reply_to_message.entities
        context.chat_data["numero"] = 0
        context.chat_data["stringa_finale"] = ""
        context.chat_data["temp_dict"] = {}
        for i in entities:
            if i.type == "text_mention":
                try:
                    context.chat_data["numero"] += 1
                    context.chat_data["stringa_finale"] += str(context.chat_data["numero"]) + ". " + "[" + i["user"]["first_name"] + "](tg://user?id=" + str(i["user"]["id"]) + "): " + \
                                  context.chat_data["role_list"][(i["user"]["first_name"], i["user"]["id"])] + "\n"
                    context.chat_data["temp_dict"][(i["user"]["first_name"], i["user"]["id"])] = context.chat_data["role_list"][(i["user"]["first_name"], i["user"]["id"])]
                except:
                    context.chat_data["numero"] += -1
        context.chat_data["stringa_finale"] += "\nNumero giocatori: *" + str(context.chat_data["numero"]) + "*"
        context.chat_data["role_list"] = context.chat_data["temp_dict"]
        context.bot.sendMessage(chat_id=update.message.chat_id, text=context.chat_data["stringa_finale"], parse_mode=telegram.ParseMode.MARKDOWN)






def sr(update, context):
    try:
        if "@" not in update.message.text[3]:
            context.chat_data["role_list"][(update.message.from_user.first_name, update.message.from_user.id)] = update.message.text[4:]
        else:
            context.bot.sendMessage(chat_id=update.message.chat_id, text="Non usare la @.")
    except NameError:
        context.bot.sendMessage(chat_id=update.message.chat_id, text="Lista non presente. Creala con /newrolelist.")


def roles(update, context):
    context.chat_data["numero"] = 0
    context.chat_data["stringa"] = ""
    for x, y in context.chat_data["role_list"].items():
        context.chat_data["numero"] += 1
        context.chat_data["stringa"] += "[" + x[0] + "](tg://user?id=" + str(x[1]) + "): " + y + "\n"
    context.chat_data["stringa"] += "\nNumero giocatori: *" + str(context.chat_data["numero"]) + "*"
    context.bot.sendMessage(chat_id=update.message.chat_id, text=context.chat_data["stringa"], parse_mode=telegram.ParseMode.MARKDOWN)


def id(update, context):
    try:
        context.bot.sendMessage(chat_id=update.message.chat_id,
                    text="```" + str(update.message.reply_to_message.from_user.id) + "```",
                    parse_mode=telegram.ParseMode.MARKDOWN)
    except AttributeError:
        update.message.reply_text("Reply to someone.")

def dr(update, context):
    if update.message.from_user.id in get_admin_ids(context, update.message.chat_id):
        try:
            context.chat_data["role_list"].pop(context.args)
            context.bot.sendMessage(chat_id=update.message.chat_id, text="Ruolo rimosso")
        except IndexError:
            try:
                context.chat_data["role_list"].pop(update.message.reply_to_message.from_user.first_name)
            except KeyError:
                context.bot.sendMessage(chat_id=update.message.chat_id, text="Giocatore non presente")


def im(update, context):
    if "immuni" in context.chat_data:
        context.chat_data["immuni"][str(update.message.from_user.id)] = update.message.from_user.first_name
        update.message.reply_text("Ora sei immune.")
        context.chat_data["are_immuni"] = True
    else:
        context.chat_data["immuni"] = {}
        im(update, context)


def lista_immuni(update, context):
    context.chat_data["stringa_imm"] = "*Lista immuni*:\n"
    for id, nome in context.chat_data["immuni"].items():
        context.chat_data["stringa_imm"] += "[" + nome + "](tg://user?id=" + id + ")\n"
    context.bot.sendMessage(chat_id=update.message.chat_id, text=context.chat_data["stringa_imm"], parse_mode=telegram.ParseMode.MARKDOWN)

def di(update, context):
    try:
        context.chat_data["immuni"].pop(str(update.message.reply_to_message.from_user.id))
    except AttributeError:
        context.chat_data["immuni"].pop(context.args)
    update.message.reply_text("Immune rimosso.")




def noim(update, context):
    if update.message.from_user.id in get_admin_ids(context, update.message.chat_id):
        context.chat_data["immuni"] = {}
        context.bot.sendMessage(chat_id=update.message.chat_id, text="Nessun immune impostato!")
        context.chat_data["are_immuni"] = False


dispatcher.add_handler(CommandHandler("bong", bong))
dispatcher.add_handler(CommandHandler("newrolelist", newrolelist))
dispatcher.add_handler(CommandHandler("sr", sr))
dispatcher.add_handler(CommandHandler("roles", roles))
dispatcher.add_handler(CommandHandler("id", id))
dispatcher.add_handler(CommandHandler("im", im))
dispatcher.add_handler(CommandHandler("immuni", lista_immuni))
dispatcher.add_handler(CommandHandler("di", di))
dispatcher.add_handler(CommandHandler("noim", noim))
dispatcher.add_handler(CommandHandler("upd", upd))
dispatcher.add_handler(CommandHandler("immuni", lista_immuni))

updater.start_polling()
