import re
from math import floor

from pypdf import PdfReader

import data_holder
from classes import *

YEAR_PATTERN = re.compile(r"^für (\d+)")
DATE_PATTERN = re.compile(r".+ (\d{2}\.\d{2}\.\d{4})")
NAME_PATTERN = re.compile(r"^ *([^,]+), ([\w ]+) {2,}")

class MetaDetector6(MetaDetector):

    def detect_meta(self, page: PageObject):
        self.client_name = ""
        self.year = 0
        self.surname = ""
        self.name = ""
        self.start = ""
        self.end = ""
        self.reset()

        page.extract_text(visitor_text=self.visitor)
        if not self._MetaDetector__check_length(self.client_name) or self.year == 0:
            return None

        pages = data_holder.get_pages()
        if page.page_number == len(pages):
            return None

        pages[page.page_number + 1].extract_text(visitor_text=self.visitor_second_page)

        if not self._MetaDetector__check_length(self.surname, self.name):
            return None
        return MetaResult(self.client_name, self.year, self.name, self.surname, self.start, self.end)

    def visitor(self, original_text: str, um, tm, font_dict, font_size):
        text = re.sub(r" +", " ", original_text.strip())
        if len(text.strip()) == 0:
            return

        y = floor(tm[5] + um[5])

        if y == 784:
            match = YEAR_PATTERN.match(text)
            if not match is None:
                self.year = match.group(1)

        if y == 810:
            self.client_name = ' '.join(text.split(" ")[:-2]) # Remove last 2 words
            return

        if y == 618 or y == 758:
            match = DATE_PATTERN.match(text)
            self.start = "" if match is None else match.group(1)

        if y == 540:
            match = DATE_PATTERN.match(text)
            self.end = "" if match is None else match.group(1)

    def visitor_second_page(self, original_text: str, um, tm, font_dict, font_size):
        if um[5] + tm[5] == 803.955:
            name_words = original_text.split(" ")
            name_words = name_words[3:-1]
            name_parts = " ".join(name_words).split(", ")
            self.surname = name_parts[0]
            self.name = name_parts[1]

# M3
if __name__ == '__main__':
    input = "D:\\Lohnkonten_geschützt\\Lohnkonten_multiple_3.pdf"

    reader = PdfReader(input, password="LoHnScuTz#1984")
    data_holder.set_pages(reader.pages)

    meta = MetaDetector6().detect_meta(reader.pages[0])
    print(f"{meta.client_name} ; {meta.year}")
    print(f"{meta.surname} ; {meta.name}")
    print(f"{meta.start} - {meta.end}")