#!/usr/bin/env python3
from json import dump
from os import listdir, getcwd

import requests

import bot_token
import collect


def tapi(method, w=False, **kwargs):
    r = requests.get(f'{url}/{method}', params=kwargs)
    if r.ok:
        data = r.json()
        if w:
            write_data(data)
        return True
    else:
        return False


def read_chats():
    if 'chats.txt' in listdir(getcwd()):
        with open('chats.txt') as f:
            return [line.strip('\n') for line in f.readlines()]
    else:
        return []


def write_chats(chats):
    with open('chats.txt', 'w') as f:
        for chat in chats:
            f.write(str(chat) + '\n')


def read_offset():
    if 'offset.txt' in listdir(getcwd()):
        with open('offset.txt') as f:
            return int(f.read())
    else:
        return 0


def write_offset(offset):
    with open('offset.txt', 'w') as f:
        f.write(str(offset))


def send_messages():
    data, diff = collect.collect_data()
    while data is None:
        data, diff = collect.collect_data()
    msgtext =  f'Дата: {collect.get_date()}\n\n\
Заражений:\n\
- Мир: {data[0]} (%2B{diff[0]})\n\
- Россия: {data[3]} (%2B{diff[3]})\n\
- Дагестан: {data[6]} (%2B{diff[6]})\n\n\
Смертей:\n\
- Мир: {data[2]} (%2B{diff[2]})\n\
- Россия: {data[5]} (%2B{diff[5]})\n\
- Дагестан: {data[8]} (%2B{diff[8]})\n\n\
Выздоровлений:\n\
- Мир: {data[1]} (%2B{diff[1]})\n\
- Россия: {data[4]} (%2B{diff[4]})\n\
- Дагестан: {data[7]} (%2B{diff[7]})\n\n\
Будьте осторожны! Берегите себя и свои семьи!\n\n\
Подписывайся на канал @seytuevru'
    if debug:
        chats = [debug_chat]
    else:
        chats = read_chats()
    sent = []
    for chat in chats:
        if chat not in sent:
            r = tapi('sendMessage', chat_id=chat, text=msgtext)
            while not r:
                r = tapi('sendMessage', chat_id=chat, text=msgtext)
            sent.append(chat)


def update_chats():
    chats = read_chats()
    offset = read_offset()

    updates = tapi('getUpdates', offset=offset)
    for update in updates['result']:
        offset = update['update_id']
        chat = update['message']['chat']
        if chat['type'] == 'group' or chat['type'] == 'supergroup':
            if str(chat['id']) not in chats:
                chats.append(chat['id'])

    write_offset(offset)
    write_chats(chats)


def write_data(data):
    with open('data.json', 'w') as f:
        dump(data, f, ensure_ascii=False, indent=2)


url = f'https://api.telegram.org/bot{bot_token.token}'
debug_chat = '-317873756'
debug = True

update_chats()
send_messages()

