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
#  или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. Подробнее см. в Афферо Стандартной
#  общественной лицензии GNU.
#
#  Вы должны были получить копию Aфферо стандартной общественной лицензии GNU
#  вместе с этой программой. Если это не так, см. http://www.gnu.org/licenses

import json
import os
import html
import re
import subprocess
import telebot

config = json.loads(open("config.json").read())

bot = telebot.TeleBot(config["token"])

USAGE = "<b>Неверный формат</b>\nИспользование: <code>/ping имя_хоста</code>"
ERROR = "<b>Произошла ошибка</b>\n{}"
OK = "<pre>{}</pre>"
WAITING = "Ожидайте…"

host_pattern = re.compile("^\w([-_\w]*\.)*[-_\w]*$|^([0-9a-f]?:?)+$", re.I)

@bot.message_handler(commands=["ping"])
def ping_pong(message):
    arguments = message.text.split()
    host = arguments[1] if len(arguments) == 2 else "<INVALID-HOST>"
    if not host_pattern.match(host):
        bot.send_message(chat_id=message.chat.id, text=USAGE,
                         parse_mode="html")
        return
    place = bot.send_message(chat_id=message.chat.id, text=WAITING,
                             parse_mode="html")
    result = subprocess.getstatusoutput("ping -c5 -- {}".format(host))
    if result[0] == 2:
        reason = result[1].split(": ")[2]
        bot.edit_message_text(chat_id=message.chat.id,
                              message_id=place.message_id,
                              text=ERROR.format(html.escape(reason)),
                              parse_mode="html")
        return
    bot.edit_message_text(chat_id=message.chat.id, message_id=place.message_id,
                          text=OK.format(html.escape(result[1])),
                          parse_mode="html")

if __name__ == "__main__":
    bot.polling()
