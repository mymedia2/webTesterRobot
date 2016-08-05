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

import collections
import html
import requests
import urllib

DESKTOP_USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0"
MOBILE_USER_AGENT = "Mozilla/5.0 (Android 4.4.4; Mobile; rv:47.0) Gecko/47.0 Firefox/47.0"

class CommonHtmlParser(html.parser.HTMLParser):

    def __init__(self):
        super().__init__()
        self.base = None
        self.depends = list()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        try:
            if tag == "base":
                self.base = attrs["href"]
            if tag == "link" and attrs["rel"] in ("stylesheet", "shortcut icon"):
                self.depends.append(attrs["href"])
            if tag in ("img", "script", "iframe"):
                self.depends.append(attrs["src"])
        except KeyError:
            pass

class WebChecker:

    class NotHtml(TypeError):
        pass

    CheckResult = collections.namedtuple("CheckResult", ["html", "css",
                                                         "script", "images"])

    def __init__(self):
        self.html_score = 0
        self.css_score = 0
        self.script_score = 0
        self.images_score = 0
        self.maximal_score = 0

    @staticmethod
    def __resolve(link, base):
        link, base = map(urllib.parse.urldefrag, (link, base))
        return urllib.parse.urljoin(base[0], link[0])

    def __check_html(self, data, url, mobi):
        if data:
            self.html_score += 1
        docs = CommonHtmlParser()
        docs.feed(data)
        base = docs.base or url
        for href in docs.depends:
            self.__check_remote_resource(self.__resolve(href, base), mobi)

    def __check_css(self, data, url):
        if data:
            self.css_score += 1
        # TODO: распарсить CSS

    def __check_js(self, data):
        if data:
            self.script_score += 1
        # Пока нет других проверок скриптов

    def __check_image(self, data):
        if data:
            self.images_score += 1
        # Пока нет других проверок картинок

    def __check_remote_resource(self, url, mobi, only_html=False):
        self.maximal_score += 1
        user_agent = MOBILE_USER_AGENT if mobi else DESKTOP_USER_AGENT
        res = requests.get(url, headers={"User-Agent": user_agent})
        if res.headers["Content-Type"].startswith("text/html"):
            self.__check_html(res.text, url, mobi)
        elif only_html:
            return False
        if res.headers["Content-Type"].startswith("text/css"):
            self.__check_css(res.text, url)
        if res.headers["Content-Type"].startswith("text/javascript"):
            self.__check_js(res.text)
        if res.headers["Content-Type"].startswith("image/svg+xml") or \
                res.headers["Content-Type"] in ("image/jpeg", "image/png"):
            self.__check_image(res.text)
        return True

    def test(self, url, mobi=False):
        if not self.__check_remote_resource(url, mobi, True):
            raise WebChecker.NotHtml
        # TODO: улучшить метод подсчёта результата
        return WebChecker.CheckResult(self.html_score / self.maximal_score,
                                      self.css_score / self.maximal_score,
                                      self.images_score / self.maximal_score,
                                      self.script_score / self.maximal_score)
