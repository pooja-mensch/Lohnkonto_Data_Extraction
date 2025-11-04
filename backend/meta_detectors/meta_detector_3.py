import re
from math import floor

from pypdf import PdfReader

from misc.classes import *

YEAR_PATTERN = re.compile(r"^für (\d+)")
DATE_PATTERN = re.compile(r".+ (\d{2}\.\d{2}\.\d{4})")
NAME_PATTERN = re.compile(r"^ *([^,]+), ([\w ]+) {2,}")
WEEKLY_HOURS_PATTERN = re.compile(r".+ (\d{1,2}[.,]\d{2})")

class MetaDetector3(MetaDetector):
    def visitor(self, original_text: str, um, tm, font_dict, font_size):
        text = re.sub(r" +", " ", original_text.strip())
        if len(text.strip()) == 0:
            return

        y = floor(tm[5] + um[5])

        if y == 784:
            match = YEAR_PATTERN.match(text)
            if not match is None:
                self.meta.year = match.group(1)

        if y == 810:
            self.meta.client_name = ' '.join(text.split(" ")[:-2]) # Remove last 2 words

        if y == 775:
            name_match = NAME_PATTERN.match(original_text)
            if not name_match is None:
                self.meta.name = name_match.group(2).strip()
                self.meta.surname = name_match.group(1).strip()

        if y == 766:
            match = DATE_PATTERN.match(text)
            self.meta.first_start = "" if match is None else match.group(1)

        if y == 758:
            match = DATE_PATTERN.match(text)
            self.meta.start = "" if match is None else match.group(1)

        if y == 749:
            match = DATE_PATTERN.match(text)
            self.meta.end = "" if match is None else match.group(1)

        if y == 723:
            match = WEEKLY_HOURS_PATTERN.match(text)
            self.meta.weekly_hours = "" if match is None else match.group(1)

# 5
if __name__ == '__main__':
    input = "E:\\MNBT\\Lohnkonten_geschützt\\Lohnkonten_Geschützt\\Lohnkonto_5.pdf"

    reader = PdfReader(input, password="LoHnScuTz#1984")
    meta = MetaDetector3().detect_meta(reader.pages[0])
    for key in meta.__dict__:
        print(f"{key} = {meta.__dict__[key]}")