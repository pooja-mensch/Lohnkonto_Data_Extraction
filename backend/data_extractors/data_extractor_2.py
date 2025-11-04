import re
from math import floor

from pypdf import PageObject

from misc.classes import DataExtractor, DataMode


class DataExtractor2(DataExtractor):

    __MONTH_PATTERN = re.compile(r"^ (1[012]| \d)")
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

        if y > 675:
            return

        if y < 330: # Sozialversicherung
            if len(text) != 88:
                return

            if not self.__detect_month(text) and not self.__second_line:
                return

            first_part = text[-21:-12]
            second_part = text[-12:-4]

            def process_part(key: str, part: str):
                if len(part.strip()) == 0:
                    return

                if self.__add or self.__is_override:
                    self.set_data(key, part, DataMode.ADD)
                else:
                    self.set_data(key, part, DataMode.SET)

            if self.__second_line:
                process_part("AV", first_part)
                process_part("PV", second_part)
            else:
                self.__add = text[5] == 'E'
                process_part("RV", first_part)
                process_part("KV", second_part)

            self.__second_line = not self.__second_line

        elif y < 675: # Lohnsteuer
            if not self.__detect_month(text):
                return

            if len(text) < 30:
                return

            brutto = text[11:25].strip().replace(".", "")
            if brutto.isdigit():
                if text[8] == 'E':
                    self.set_data("BRUTTO", brutto, DataMode.ADD)
                else:
                    self.set_data("BRUTTO", brutto, DataMode.SET)

    def process_page(self, page: PageObject, start_page: bool):
        self.__is_start_page = start_page
        self.__second_line = False
        self.__add = False
        self.__is_override = False
        self.month = -1
        page.extract_text(visitor_text=self.__visitor)