import re
from math import floor

from pypdf import PdfReader

from misc.classes import MetaDetector

YEAR_PATTERN = re.compile(r"^\d+ (\d+)")
DATE_PATTERN = re.compile(r".+ (\d{2}\.\d{2}\.\d{4})")
WEEKLY_HOURS_PATTERN = re.compile(r".+ (\d{1,2}[.,]\d{2})")

class MetaDetector1(MetaDetector):

    client_line = ""
    surname_line = ""

    def reset(self):
        self.client_line = ""
        self.surname_line = ""

    def visitor(self, text: str, um, tm, font_dict, font_size):
        text = re.sub(r" +", " ", text.strip())
        if len(text.strip()) == 0:
            return

        y = floor(tm[5] + um[5])

        if y == 785:
            match = YEAR_PATTERN.match(text)
            if not match is None:
                self.meta.year = match.group(1)

        if y == 776:
            self.client_line = text
            return

        if y == 734 and self.client_line != "":
            self.surname_line = text
            match = DATE_PATTERN.match(text)
            self.meta.first_start = "" if match is None else match.group(1)

        if (y == 725 or y == 726) and self.surname_line != "":
            surname_words = self.surname_line.split(" ")
            next_word = 0
            surname_buffer = surname_words[0].strip()
            surname_buffer_temp = surname_buffer
            while surname_buffer_temp in self.client_line and next_word < len(surname_words) - 1:
                surname_buffer = surname_buffer_temp
                next_word += 1
                surname_buffer_temp = surname_buffer + " " + surname_words[next_word].strip()

            self.meta.surname = surname_buffer
            surname_start = self.client_line.find(self.meta.surname)
            self.meta.client_name = self.client_line[:surname_start]
            self.meta.client_name = self.meta.client_name[len(self.meta.client_name.split(" ")[0]):].strip() # Remove "Mandant"

            name_words = text.split(" ")
            next_word = 0
            name_buffer = name_words[0].strip()
            name_buffer_temp = name_buffer
            while name_buffer_temp in self.client_line and next_word < len(name_words) - 1:
                name_buffer = name_buffer_temp
                next_word += 1
                name_buffer_temp = name_buffer + " " + name_words[next_word].strip()

            self.meta.name = name_buffer

        if len(self.meta.name) != 0 and text.startswith(self.meta.name):
            self.meta.start = text[len(self.meta.name) : len(self.meta.name) + 11].strip()

        if y == 709:
            match = WEEKLY_HOURS_PATTERN.match(text)
            self.meta.weekly_hours = "" if match is None else match.group(1)

        if self.client_line != "" and y == 717:
            match = DATE_PATTERN.match(text)
            self.meta.end = "" if match is None else match.group(1)

# 1, 2, 6
if __name__ == '__main__':
    input = "E:\\MNBT\\Lohnkonten_geschützt\\Lohnkonten_Geschützt\\Lohnkonto Prio 2.pdf"
    template = "Lohnkonten_Projekt_Vorlage.xlsx"

    reader = PdfReader(input, password="LoHnScuTz#1984")
    meta = MetaDetector1().detect_meta(reader.pages[34])
    for key in meta.__dict__:
        print(f"{key} = {meta.__dict__[key]}")