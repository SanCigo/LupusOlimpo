from telethon import TelegramClient, tl, events
import logging
from telethon.tl.types import ChannelParticipantsAdmins
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
api_id = 0  # api id here
api_hash = ""  # api hash here
client = TelegramClient('anon', api_id, api_hash)

import os



script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)


# admins
with open("admins.txt", "r") as f:
    lista_admin = f.read()


starting = False
pinon = False
first_night = True
lista = []  # LISTA DEI GRUPPI
'''Parallelismo serve a far sì che il bot possa lavorare le sue variabili in gruppi diversi senza interferire con quelle
altrui. Questo perché ogni definizione viene fatta all'interno del dizionario al relativo chat_id'''
parallelismo = {"group_id": [starting, pinon, lista_admin[:], first_night]}
assert lista, "Lista non dovrebbe essere vuota."


# 175844556 is Telegram id for Werewolf Moderator
@client.on(events.NewMessage(chats=lista, pattern=r'\#players', from_users=175844556))
async def starting_spin(event):
    temp = event.chat_id
    global parallelismo
    parallelismo[str(event.chat_id)][0] = True
    if parallelismo[str(event.chat_id)][1]:
        await event.reply("/spin")
        parallelismo[str(event.chat_id)][3] = True


@client.on(events.NewMessage(chats=lista, pattern=r'Giocatori in vita:', from_users=175844556))
async def starting_upd(event):
    if parallelismo[str(event.chat_id)][0]:
        parallelismo[str(event.chat_id)][0] = False
        await event.reply("/newrolelist")
    elif 'Durata della partita:' not in event.raw_text and parallelismo[str(event.chat_id)][3]:
        await event.reply("/upd")
        await event.respond("/noim")
        parallelismo[str(event.chat_id)][3] = False
    elif 'Durata della partita:' not in event.raw_text:
        await event.reply("/upd")



@client.on(events.NewMessage(pattern=r'p1non'))
async def p1non(event):
    if event.from_id in parallelismo[str(event.chat_id)][2]:
        parallelismo[str(event.chat_id)][1] = True
        await event.respond("Pinon!")


@client.on(events.NewMessage(pattern=r'p1noff'))
async def p1noff(event):
    if event.from_id in parallelismo[str(event.chat_id)][2]:
        parallelismo[str(event.chat_id)][1] = False
        await event.respond("Pinoff!")

@client.on(events.NewMessage(pattern=r'^Test'))
async def test(event):
    if event.from_id in parallelismo[str(event.chat_id)][2]:
        await event.reply("Toast!")



@client.on(events.NewMessage(pattern=r'^/adminreload'))
async def adminreload(event):
    if event.from_id in parallelismo[str(event.chat_id)][2]:
        parallelismo[str(event.chat_id)][2] = []
        async for user in client.iter_participants(await event.get_input_chat(), filter=ChannelParticipantsAdmins,
                                                   aggressive=True):
            parallelismo[str(event.chat_id)][2].append(user.id)
        await event.reply("Lista admin aggiornata.")


@client.on(events.ChatAction())
async def entrata(event):
    if event.user_joined:
        await event.reply("/stats@wwstatbot")


client.start()
client.run_until_disconnected()
