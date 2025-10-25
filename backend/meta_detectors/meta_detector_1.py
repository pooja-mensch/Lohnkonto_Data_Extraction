import re
from math import floor

from pypdf import PdfReader

from classes import MetaDetector

YEAR_PATTERN = re.compile(r"^\d+ (\d+)")
DATE_PATTERN = re.compile(r".+ (\d{2}\.\d{2}\.\d{4})")

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
                self.year = match.group(1)

        if y == 776:
            self.client_line = text
            return

        if y == 734 and self.client_line != "":
            self.surname_line = text

        if (y == 725 or y == 726) and self.surname_line != "":
            surname_words = self.surname_line.split(" ")
            next_word = 0
            surname_buffer = surname_words[0].strip()
            surname_buffer_temp = surname_buffer
            while surname_buffer_temp in self.client_line and next_word < len(surname_words) - 1:
                surname_buffer = surname_buffer_temp
                next_word += 1
                surname_buffer_temp = surname_buffer + " " + surname_words[next_word].strip()

            self.surname = surname_buffer
            surname_start = self.client_line.find(self.surname)
            self.client_name = self.client_line[:surname_start]
            self.client_name = self.client_name[len(self.client_name.split(" ")[0]):].strip() # Remove "Mandant"

            name_words = text.split(" ")
            next_word = 0
            name_buffer = name_words[0].strip()
            name_buffer_temp = name_buffer
            while name_buffer_temp in self.client_line and next_word < len(name_words) - 1:
                name_buffer = name_buffer_temp
                next_word += 1
                name_buffer_temp = name_buffer + " " + name_words[next_word].strip()

            self.name = name_buffer

        if len(self.name) != 0 and text.startswith(self.name):
            self.start = text[len(self.name) : len(self.name) + 11].strip()

        if self.client_line != "" and y == 717:
            match = DATE_PATTERN.match(text)
            self.end = "" if match is None else match.group(1)

# 1, 2, 6
if __name__ == '__main__':
    input = "D:\\Lohnkonten_geschützt\\Lohnkonto Prio 2.pdf"
    template = "Lohnkonten_Projekt_Vorlage.xlsx"

    reader = PdfReader(input, password="LoHnScuTz#1984")
    meta = MetaDetector1().detect_meta(reader.pages[0])
    print(f"{meta.client_name} ; {meta.year}")
    print(f"{meta.surname} ; {meta.name}")
    print(f"{meta.start} - {meta.end}")