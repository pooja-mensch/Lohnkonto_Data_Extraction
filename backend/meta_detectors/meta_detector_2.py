import re
from math import floor

from pypdf import PdfReader

from classes import *

YEAR_PATTERN = re.compile(r"^für (\d+)")
DATE_PATTERN = re.compile(r".+ (\d{2}\.\d{2}\.\d{4})")
NAME_PATTERN = re.compile(r"^ *([^,]+), ([\w ]+) {2,}")

class MetaDetector2(MetaDetector):

    def visitor(self, original_text: str, um, tm, font_dict, font_size):
        text = re.sub(r" +", " ", original_text.strip())
        if len(text.strip()) == 0:
            return

        y = floor(tm[5] + um[5])

        if y == 780:
            match = YEAR_PATTERN.match(text)
            if not match is None:
                self.year = match.group(1)

        if y == 807:
            self.client_name = ' '.join(text.split(" ")[:-2]) # Remove last 2 words
            return

        if y == 771:
            nameMatch = NAME_PATTERN.match(original_text)
            if not nameMatch is None:
                self.name = nameMatch.group(2).strip()
                self.surname = nameMatch.group(1).strip()

        if y == 753:
            match = DATE_PATTERN.match(text)
            self.start = "" if match is None else match.group(1)

        if y == 744:
            match = DATE_PATTERN.match(text)
            self.end = "" if match is None else match.group(1)

# 3
if __name__ == '__main__':
    input = "D:\\Lohnkonten_geschützt\\Lohnkonto_3.pdf"

    reader = PdfReader(input, password="LoHnScuTz#1984")
    meta = MetaDetector2().detect_meta(reader.pages[0])
    print(f"{meta.client_name} ; {meta.year}")
    print(f"{meta.surname} ; {meta.name}")
    print(f"{meta.start} - {meta.end}")