import re
from math import floor

from pypdf import PageObject

from misc.classes import DataExtractor, DataMode


class DataExtractor6(DataExtractor):

    __MONTH_PATTERN = re.compile(r"^(1[012]|\d)[^.]")
    __CHANGE_PATTERN = re.compile(r"([\d.+-]+)$")

    __is_start_page = False
    __second_line = False
    __add = False

    def __detect_month(self, text: str):
        month_match = self.__MONTH_PATTERN.match(text)
        if not month_match is None:
            self.month = int(month_match.group(1)) - 1
            return True
        return False

    def __visitor(self, text: str, um, tm, font_dict, font_size):
        if not self.__is_start_page:
            return

        if len(text.strip()) == 0:
            return

        y = floor(tm[5] + um[5])

        if y > 670 or font_size != 9.504:
            return

        if y < 340: # Sozialversicherung
            if not self.__detect_month(text) and not self.__second_line:
                return

            words = text.strip().split(" ")
            if len(words) < 7:
                return

            def process_part(key: str, part: str):
                if len(part.strip()) == 0:
                    return

                if self.__add:
                    self.set_data(key, part, DataMode.ADD)
                else:
                    self.set_data(key, part, DataMode.SET)

            if len(words) > 10:
                for word in reversed(text.split(" ")):
                    if len(word) <= 3:
                        continue

                    if self.__second_line:
                        process_part("AV", word)
                    else:
                        self.__add = text.find("E") != -1 and text.find("E") < len(text) / 3
                        process_part("RV", word)
                    break
            else:
                i = 0
                for word in reversed(text.split(" ")):
                    i -= 1
                    if len(word) <= 3:
                        continue

                    if self.__second_line:
                        process_part("AV", words[:i - 1])
                        process_part("PV", words[:i])
                    else:
                        self.__add = text.find("E") != -1 and text.find("E") < len(text) / 3
                        process_part("RV", words[:i - 1])
                        process_part("KV", words[:i])

            self.__second_line = not self.__second_line

        else: # Lohnsteuer
            if not self.__detect_month(text):
                return

            if len(text) < 30:
                return

            for word in text.split(" "):
                if len(word) <= 3:
                    continue

                brutto = word.strip().replace(".", "")
                if brutto.isdigit():
                    if "E" in text:
                        self.set_data("BRUTTO", brutto, DataMode.ADD)
                    else:
                        self.set_data("BRUTTO", brutto, DataMode.SET)
                break

    def process_page(self, page: PageObject, start_page: bool):
        self.__is_start_page = start_page
        self.__second_line = False
        self.__add = False
        page.extract_text(visitor_text=self.__visitor)