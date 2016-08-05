#!/usr/bin/python
#
#  Этот файл — часть webTesterRobot.
#  Copyright (C) 2016  Николай Гурьев
#
#  webTesterRobot — свободная программа: вы можете перераспространять её и/или
#  изменять её на условиях Афферо стандартной общественной лицензии GNU в том
#  виде, в каком она была опубликована Фондом свободного программного
#  обеспечения; либо версии 3 лицензии, либо (по вашему выбору) любой более
#  поздней версии.
#
#  webTesterRobot распространяется в надежде, что он будет полезным,
#  но БЕЗО ВСЯКИХ ГАРАНТИЙ; даже без неявной гарантии ТОВАРНОГО ВИДА
#  или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. Подробнее см. в Афферо стандартной
#  общественной лицензии GNU.
#
#  Вы должны были получить копию Aфферо стандартной общественной лицензии GNU
#  вместе с этой программой. Если это не так, см. http://www.gnu.org/licenses

import emoji
import html
import os
import re
import subprocess
import telebot
import urllib3

PING_OK = "<pre>{}</pre>"
PING_USAGE = """\
<b>Неверный формат</b>
Использование: <code>/ping имя_хоста</code>
"""
ERROR = """\
<b>Произошла ошибка</b>
{}
"""
DEPENDS = """\
<b>Внутренняя ошибка</b>
Не установлены зависимости
"""
TEST_OK = emoji.emojize("Ресурс доступен :white_heavy_check_mark:")
TEST_EMPTY = emoji.emojize("Пустой ответ :warning_sign:")
TEST_FAIL = emoji.emojize("Ресурс не доступен :cross_mark:")
TEST_USAGE = """
<b>Неверный формат</b>
Использование: <code>/test адрес_ресурса</code>
"""
WAITING = "Ожидайте…"
HELLO = "Привет! Пока я умею работать лишь с двумя командами: /test и /ping"

bot = telebot.TeleBot(os.environ["BOT_TOKEN"])

host_pattern = re.compile("^\w([-_\w]*\.)*[-_\w]*$|^([0-9a-f]?:?)+$", re.I)

http = urllib3.PoolManager()
http.headers["User-Agent"] = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0"

@bot.message_handler(commands=["start"])
def helper(message):
    bot.send_message(chat_id=message.chat.id, text=HELLO)

@bot.message_handler(commands=["test"])
def testing(message):
    arguments = message.text.split()
    if len(arguments) != 2:
        bot.send_message(chat_id=message.chat.id, text=TEST_USAGE,
                         parse_mode="html")
        return
    url = arguments[1]
    place = bot.send_message(chat_id=message.chat.id, text=WAITING)
    try:
        response = http.request("GET", url, preload_content=False)
    except urllib3.exceptions.HTTPError:
        bot.edit_message_text(chat_id=message.chat.id,
                              message_id=place.message_id, text=TEST_FAIL)
        return
    if response.headers.get("Content-Length") != 0 and response.read(1) == b'':
        bot.edit_message_text(chat_id=message.chat.id,
                              message_id=place.message_id, text=TEST_EMPTY)
        return
    bot.edit_message_text(chat_id=message.chat.id, message_id=place.message_id,
                          text=TEST_OK)

@bot.message_handler(commands=["ping"])
def ping_pong(message):
    arguments = message.text.split()
    host = arguments[1] if len(arguments) == 2 else "<INVALID-HOST>"
    if not host_pattern.match(host):
        bot.send_message(chat_id=message.chat.id, text=PING_USAGE,
                         parse_mode="html")
        return
    # Не нравится эта идея. Надо избавиться от этой проверки в этом месте
    if os.system("which ping > /dev/null") != 0:
        bot.send_message(chat_id=message.chat.id, text=DEPENDS,
                         parse_mode="html")
        return
    place = bot.send_message(chat_id=message.chat.id, text=WAITING)
    result = subprocess.getstatusoutput("LANG=ru_RU.UTF-8 ping -c5 -- {}"
                                        .format(host))
    if result[0] == 2:
        reason = result[1].split(": ")[2]
        bot.edit_message_text(chat_id=message.chat.id,
                              message_id=place.message_id,
                              text=ERROR.format(html.escape(reason)),
                              parse_mode="html")
        return
    bot.edit_message_text(chat_id=message.chat.id, message_id=place.message_id,
                          text=PING_OK.format(html.escape(result[1])),
                          parse_mode="html")
