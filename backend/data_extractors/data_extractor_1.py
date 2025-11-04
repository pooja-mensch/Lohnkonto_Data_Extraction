import re
from math import floor

from pypdf import PageObject

from misc.classes import DataExtractor, DataMode


class DataExtractor1(DataExtractor):

    __MONTH_PATTERN = re.compile(r"^\*?(1[012]|0\d)(?:\d{2})?")
    __CHANGE_PATTERN = re.compile(r"([\d.+-]+)$")
    __DATE_PATTERN = re.compile(r"(\d{2}\.\d{2}\.\d{4})")

    __previousLine = ""
    __dataType = ""
    __expectData = False
    __override = False
    __ovline = ""

    def __detect_month(self, text: str):
        if not self.__DATE_PATTERN.match(text) is None:
            return False

        monthMatch = self.__MONTH_PATTERN.match(text)
        if not monthMatch is None:
            self.month = int(monthMatch.group(1)) - 1
            return True
        return False

    def __visitor(self, text: str, um, tm, font_dict, font_size):
        text = re.sub(r" +", " ", text.strip())
        if len(text.strip()) == 0:
            return

        y = floor(um[5] + tm[5])

        if (text == "Lohnsteuer" or text == "Sozialversicherung") and font_size == 9.3:
            self.__dataType = text
            return

        if text.startswith("**"):
            self.__dataType = ""
            return

        if y <= 220:
            return

        if self.__dataType == "Lohnsteuer":
            def processLine(text: str, usingPrevious: bool, forceAdd: bool):
                if self.__detect_month(text):
                    words = text.split(" ")
                    if not usingPrevious and len(words) <= 5:
                        if "NZ" in text:
                            self.__previousLine = text
                        return

                    for i, word in enumerate(words):
                        if i == 0: continue

                        match = self.__CHANGE_PATTERN.match(word)
                        if match is None: continue

                        data = match.group(1)
                        data = data.replace(".", "")
                        if data[-1] == "-":
                            self.set_data("BRUTTO", data[:-1], DataMode.SUB)
                        elif data[-1] == "+":
                            self.set_data("BRUTTO", data[:-1], DataMode.ADD)
                        else:
                            self.set_data("BRUTTO", data, DataMode.ADD if forceAdd else DataMode.SET)
                        return

            if not self.__previousLine is None:
                 processLine(self.__previousLine, True, text.startswith("E"))
                 self.__previousLine = None

            processLine(text, False, False)
            return

        if self.__dataType == "Sozialversicherung":
            if self.__expectData:
                self.__expectData = False

                words = text.split(" ")

                def process(key: str, word: str, mode: DataMode):
                    if word.endswith("-"):
                        word = word[:-1]
                        mode = DataMode.SUB
                    self.set_data(key, word, mode)

                if self.__override:
                    self.__override = False
                    offset = 0 if words[-1].isdigit() else 1

                    if len(words) == 1:
                        process("RV", words[-1], DataMode.ADD)
                    elif len(words) <= 8:
                        if "KV" in self.months[self.month]:
                            process("PV", words[-1 - offset], DataMode.ADD)
                            process("RV", words[-2 - offset], DataMode.ADD)
                            process("KV", words[-3 - offset], DataMode.ADD)
                        else:
                            process("AV", words[-1 - offset], DataMode.ADD)
                            process("RV", words[-2 - offset], DataMode.ADD)
                    else:
                        process("PV", words[-1 - offset], DataMode.ADD)
                        process("AV", words[-2 - offset], DataMode.ADD)
                        process("RV", words[-3 - offset], DataMode.ADD)
                        process("KV", words[-4 - offset], DataMode.ADD)
                    return

                if self.__detect_month(text):
                    return

                if len(words) <= 3:
                    return

                if len(words) <= 10:
                    self.set_data("AV", words[-2], DataMode.SET)
                    self.set_data("RV", words[-3], DataMode.SET)
                    self.set_data("PV", "", DataMode.SET)
                    self.set_data("KV", "", DataMode.SET)
                else:
                    self.set_data("PV", words[-2], DataMode.SET)
                    self.set_data("KV", words[-5], DataMode.SET)
                    self.set_data("AV", words[-3], DataMode.SET)
                    self.set_data("RV", words[-4], DataMode.SET)

            elif self.__detect_month(text):
                self.__ovline = text
                self.__expectData = True
            elif ((text.startswith("* ") and not text.startswith("* = ")) or (text.startswith("E "))) and "AV" in self.months[self.month]:
                self.__ovline = text
                self.__expectData = True
                self.__override = True

    def process_page(self, page: PageObject, _start_page: bool):
        self.__dataType = ""
        self.__expectData = False
        self.__override = False
        page.extract_text(visitor_text=self.__visitor)