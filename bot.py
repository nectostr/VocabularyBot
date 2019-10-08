#!/usr/bin/python
# -*- coding: windows-1251 -*-

import config
import telebot
import datetime
import logging
import sqlite3
import re
import random
import time
import pyodbc

logging.basicConfig(level=logging.INFO)
mplLogger = logging.getLogger("matplotlib")
mplLogger.setLevel(logging.WARNING)
DATABASE = '.\mydatabase.db'
if config.use_proxy:
    telebot.apihelper.proxy = {'https': 'socks5h://{}:{}@{}:{}'.format(config.proxy_user,
                                                                      config.proxy_pass,
                                                                      config.proxy_address,
                                                                      config.proxy_port)}

bot = telebot.TeleBot(config.token)

local_words_storage = []
adding_words = 0
current_word = ''
deleting_ticket = 0
sending_now = False
wait_time = 60#5*60
example_mode = False
TABLE_NAME = 'WORDS'

@bot.message_handler(commands=["start"])
def send_welcome(message):
    logging.debug('start command incoming')
    bot.reply_to(message, r"""I am trying to help you, idiot, to work with new words. I have such comands:
                            /start - do nothing, just lol you
                            /add_words_mode - to begin adding new words and then to end
                            /example_mode - to filling or not examples in adding words
                            /learning - to start learning
                            /stop_learning - just gues what it coluld be for
                            /change_learning_rate - change speed of remembering you the word""")

@bot.message_handler(commands=["example_mode"])
def send_welcome(message):
    logging.debug('example mode changed')
    global example_mode
    example_mode = not example_mode
    if example_mode:
        ans = r"""Now, while you adding words you WILL fill examples to"""
    else:
        ans = r"""Now, while you adding words you WON'T fill examples to"""
    bot.reply_to(message, ans)


@bot.message_handler(commands=["add_words_mode"])
def add_words(message):
    global adding_words
    global local_words_storage
    if adding_words == 0:
        logging.debug('Adding words')
        adding_words = 1
        local_words_storage = []
        bot.reply_to(message, "I am waiting english-russian message, when you want to stop send this command again")
    else:
        logging.debug('Stopping adding words, db ad initiate')
        adding_words = 0
        send_to_db(local_words_storage)
        local_words_storage = []
        logging.debug('db fin')
        bot.send_message(message.chat.id, "Done, my commandor, /learning, when you are ready")

@bot.message_handler(commands=["stop_learning"])
def add_words(message):
    global sending_now
    sending_now = False
    bot.reply_to(message, "Yep, as you wish, my treasure! \n<3")


@bot.message_handler(commands=["learning"])
def send_words(message):
    global adding_words
    global wait_time
    global sending_now
    sending_now = True
    logging.debug('Learning begins')
    words = get_voc_from_db()
    while sending_now:
        word = random.choice(words)
        sentence = word[0] + word[1] + '\n\n' + word[2]
        bot.send_message(message.chat.id, sentence)
        time.sleep(wait_time)

@bot.message_handler(commands=["change_learning_rate"])
def change_learning_rate(message):
    global adding_words
    adding_words = "learning_rate"
    bot.reply_to(message, "Send me what time should i wait till next word in seconds")


@bot.message_handler(content_types=["text"])
def handle_text(message):
    global adding_words
    global current_word
    logging.debug('some text accepted')
    if adding_words == 1:
        current_word = message.text
        if example_mode:
            adding_words = 2
            bot.send_message(message.chat.id, "Great, now get me an example")
        else:
            rus = re.search("""([А-Яа-яЁё].*)""", current_word)
            eng = re.search("""(.*)[А-Яа-яЁё]""", current_word)
            if rus != None and eng != None:
                local_words_storage.append((eng[0], rus[0], ""))
                bot.send_message(message.chat.id, "Done, next")
            else:
                rus = re.search("""(.*)\-""", current_word)
                eng = re.search("""\-(.*)""", current_word)
                local_words_storage.append((eng.group(1), rus.group(1), ""))
                bot.reply_to(message, "This is not translation, you get? I've added, but")
    elif adding_words == 2 and example_mode:
        desc = message.text
        rus = re.search("""([А-Яа-яЁё].*)""", current_word)
        eng = re.search("""(.*)[А-Яа-яЁё]""", current_word)
        if rus != None and eng != None:
            local_words_storage.append((eng[0], rus[0], desc))
            bot.send_message(message.chat.id, "Done, next")
        else:
            rus = re.search("""(.*)\-""", current_word)
            eng = re.search("""\-(.*)""", current_word)
            local_words_storage.append((eng.group(1), rus.group(1), desc))
            bot.reply_to(message, "This is not translation, you get? I've added, but")
        local_words_storage.append((eng, rus, desc))
        adding_words = 1
        bot.send_message(message.chat.id, "Done, now next")
    elif adding_words == "learning_rate":
        adding_words = 0
        global wait_time
        if message.text.isdigit():
            wait_time = int(message.text)
            bot.reply_to(message, "Brilliant, you are so quick")
        else:
            bot.reply_to(message, "That is not a number in secs, try again from sending command")
    else:
        bot.reply_to(message, "I don't get what is going on now.")

def send_to_db(list_to_add):
    global conn
    global TABLE_NAME
    try:
        cursor = conn.cursor()
        res = cursor.execute(f""" SELECT *
                              FROM main.{TABLE_NAME} """)

        r = res.fetchall()
        list_to_add = list(set(list_to_add) - set([row[0] for row in r]))
        if list_to_add:
            cursor.executemany(f""" INSERT INTO main.{TABLE_NAME} 
                                VALUES(?, ?, ?) """,
                               list_to_add)
        conn.commit()
        cursor.close()
    except:
        logging.critical("Commiting the word gone wrong")

def get_voc_from_db():
    global conn
    global TABLE_NAME
    try:
        cursor = conn.cursor()
        res = cursor.execute(f""" SELECT *
                            FROM main.{TABLE_NAME} """)

        r = res.fetchall()
        cursor.close()
    except:
        logging.critical("Commiting the word gone wrong")
        raise
    return r

def get_or_create_the_DB():
    global TABLE_NAME
    conn = sqlite3.connect("mydatabase.db")
    cursor = conn.cursor()
    try:
        a = cursor.execute(f"SELECT * FROM {TABLE_NAME}").fetchall()
    except sqlite3.OperationalError:
        TABLE_NAME = "WORDS"
        cursor.execute(f""" CREATE TABLE {TABLE_NAME}
                              (english text, russian text,
                               example text)
                           """)
        conn.commit()
    except:
        logging.CRITICAL("Oh god no, why db is down??")
        raise
    finally:
        cursor.close()
        conn.close()
    conn = pyodbc.connect("DRIVER=SQLITE3;DATABASE={};username=;".format(DATABASE))

    return conn



if __name__ == '__main__':
    # print(a, b)
    conn = get_or_create_the_DB()
    cursor = conn.cursor()
    bot.polling(none_stop=True)