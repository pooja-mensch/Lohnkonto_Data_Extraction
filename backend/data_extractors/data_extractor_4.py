import re

from pypdf import PageObject

from classes import DataExtractor, DataMode


class DataExtractor4(DataExtractor):

    __MONTH_PATTERN = re.compile(r"^\*?(1[012]|0\d)(?:\d{2})?")
    __CHANGE_PATTERN = re.compile(r"([\d.+-]+)$")

    __dataType = ""
    __expectData = False

    def __detect_month(self, text: str):

        monthMatch = self.__MONTH_PATTERN.match(text)
        if not monthMatch is None:
            self.month = int(monthMatch.group(1)) - 1
            return True
        return False

    def __visitor(self, text: str, um, tm, font_dict, font_size):
        text = re.sub(r" +", " ", text.strip())
        if len(text.strip()) == 0:
            return

        if (text == "Lohnsteuer" or text == "Sozialversicherung") and font_size == 9.3:
            self.__dataType = text
            return

        if text.startswith("**"):
            self.__dataType = ""
            return

        if self.__dataType == "Lohnsteuer":
            if self.__detect_month(text):
                words = text.split(" ")
                if len(words) <= 5:
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
                        self.set_data("BRUTTO", data[:-1], DataMode.SET)
                    return

        if self.__dataType == "Sozialversicherung":
            if self.__expectData:
                self.__expectData = False
                words = text.split(" ")

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

            elif self.__detect_month(text) and "BRUTTO" in self.months[self.month]:
                self.__expectData = True

    def process_page(self, page: PageObject, _start_page: bool):
        self.__dataType = ""
        self.__expectData = False
        page.extract_text(visitor_text=self.__visitor)