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

import requests

from html.parser import HTMLParser

DESKTOP_USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0"
MOBILE_USER_AGENT = "Mozilla/5.0 (Android 4.4.4; Mobile; rv:47.0) Gecko/47.0 Firefox/47.0"

class CommonHtmlParser(HTMLParser):

	def __init__(self):
		super().__init__()
		self.links = list()

	def handle_starttag(self, tag, attrs):
		attrs = dict(attrs)
		if tag == "link" and attrs["rel"] in ("stylesheet", "shortcut icon"):
			self.links.append(attrs["href"])
		if tag in ("img", "script", "iframe") and "src" in attrs:
			self.links.append(attrs["src"])
		print("Start tag:", tag)
		for attr in attrs.items():
			print("     attr:", attr)

	def handle_endtag(self, tag):
		print("End tag  :", tag)

	def handle_data(self, data):
		print("Data     :", data)

	def handle_comment(self, data):
		print("Comment  :", data)

	def handle_decl(self, data):
		print("Decl     :", data)

class VkWatcher:
	class InnerParser(CommonHtmlParser):
		pass

	def check_web_page(self, url):
		res = requests.get(url, headers={"User-Agent": DESKTOP_USER_AGENT})
		if not res.headers["Content-Type"].startswith("text/html"):
			return False
		parser = VkWatcher.InnerParser()
		parser.feed(res.text)
		print("result:   ", parser.links)
		return True

if __name__ == "__main__":
	VkWatcher().check_web_page("https://vk.com")
