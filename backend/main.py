import sys
import time
import warnings
from copy import copy
from math import floor, ceil

from openpyxl import load_workbook
from pypdf import PdfReader, PasswordType

import data_holder
from classes import Person
from data_extractors.data_extractor_1 import DataExtractor1
from data_extractors.data_extractor_2 import DataExtractor2
from data_extractors.data_extractor_3 import DataExtractor3
from data_extractors.data_extractor_4 import DataExtractor4
from data_extractors.data_extractor_5 import DataExtractor5
from data_extractors.data_extractor_6 import DataExtractor6
from data_extractors.data_extractor_7 import DataExtractor7
from data_holder import *
from meta_detectors.meta_detector_1 import MetaDetector1
from meta_detectors.meta_detector_2 import MetaDetector2
from meta_detectors.meta_detector_3 import MetaDetector3
from meta_detectors.meta_detector_4 import MetaDetector4
from meta_detectors.meta_detector_5 import MetaDetector5
from meta_detectors.meta_detector_6 import MetaDetector6
from meta_detectors.meta_detector_7 import MetaDetector7

detectors = { # PyInstaller messes with reflection based access
    MetaDetector1(): DataExtractor1(),
    MetaDetector2(): DataExtractor2(),
    MetaDetector3(): DataExtractor3(),
    MetaDetector4(): DataExtractor4(),
    MetaDetector5(): DataExtractor5(),
    MetaDetector6(): DataExtractor6(),
    MetaDetector7(): DataExtractor7(),
}

people = []

def __push_people(months):
    people.append(Person(
        get_current_meta().name,
        get_current_meta().surname,
        get_current_meta().start,
        get_current_meta().end,
        copy(months)
    ))

def __main():
    pdf_file = sys.argv[1]
    template = sys.argv[2]

    reader = PdfReader(pdf_file)
    if reader.is_encrypted:
        print("[INFO] Diese Datei benötigt ein Password, bitte gib es ein:")
        while True:
            password = input()
            if reader.decrypt(password=password) != PasswordType.NOT_DECRYPTED:
                break

            print("[FEHLER] Falsches Passwort.")

    data_holder.set_pages(reader.pages)
    data_holder.set_pages(reader.pages)

    meta_detector = None
    data_extractor = None
    meta = None

    for detector in detectors.keys():
        meta = detector.detect_meta(reader.pages[0])
        if not meta is None:
            meta_detector = detector
            data_extractor = detectors[detector]
            print(f"[INFO] Erkanntes Format: {detector.__class__.__name__[len("MetaDetector"):]}")
            break

    if meta_detector is None:
        print("[FEHLER] Dieses Format wird derzeit nicht unterstützt.")
        return


    start = time.time()

    year = meta.year
    client_name = meta.client_name
    print(f"[INFO] Klient: {client_name}")
    print(f"[INFO] Jahr: {year}")

    previous_percent = -1

    for page in reader.pages:
        set_current_page(page.page_number)
        percent = (page.page_number * 20 / len(reader.pages)).__floor__() * 5 # Percentage, rounded to 5% increments
        if percent > previous_percent:
            previous_percent = percent
            print(f"{percent}%")

        meta = meta_detector.detect_meta(page)
        start_page = False
        if not meta is None:
            start_page = True
            if year != meta.year or client_name != meta.client_name:
                print(f"[ERROR] Meta mismatch: {year} != {meta.year} or {client_name} != {meta.client_name}")
                return

            if not get_current_meta() is None and (meta.surname != get_current_meta().surname or meta.name != get_current_meta().name):
                months = data_extractor.months
                __push_people(months)
                data_extractor.month = -1
                for i in range(0, len(months)):
                    months[i] = {}
            set_current_meta(meta)

        data_extractor.process_page(page, start_page)

    __push_people(data_extractor.months)
    print("100%")

    with warnings.catch_warnings(action="ignore"):
        workbook = load_workbook(template)
    data = workbook['IST Gehälter']
    project = workbook['Projektübersicht']

    project['B1'] = client_name
    project['B5'] = "01.01." + str(year)
    data['D4'] = ""

    file = 1

    i = 4
    for person in people:
        if i - 4 >= 30: # Too many employees, generate another xlsx file
            workbook.save(f'{client_name} {file}.xlsx')
            with warnings.catch_warnings(action="ignore"):
                workbook = load_workbook(template)
            data = workbook['IST Gehälter']
            project = workbook['Projektübersicht']
            project['B1'] = client_name
            project['B5'] = "01.01." + str(year)
            data['D4'] = ""
            i = 4
            file += 1

        projectColumn = str(i - 1)
        column = str(i)

        project["E" + projectColumn] = person.name
        data["B" + column] = person.name
        project["F" + projectColumn] = person.surname
        data["C" + column] = person.surname
        project["G" + projectColumn] = person.start
        data["E" + column] = person.start
        project["H" + projectColumn] = person.end
        data["F" + column] = person.end

        def getCellValue(month, key):
            value = month[key] if key in month else 0

            if value == "":
                return value
            else:
                return value / 100 # Value is in cents

        monthCounter = 0
        for __month in person.months:
            if "BRUTTO" in __month:
                data.cell(row=i, column=monthCounter + 7, value=getCellValue(__month, "BRUTTO"))
                data.cell(row=i, column=monthCounter + 33, value=getCellValue(__month, "RV"))
                data.cell(row=i, column=monthCounter + 46, value=getCellValue(__month, "AV"))
                data.cell(row=i, column=monthCounter + 59, value=getCellValue(__month, "KV"))
                data.cell(row=i, column=monthCounter + 72, value=getCellValue(__month, "PV"))
            monthCounter += 1
        i += 1

    if file == 1:
        workbook.save(f'{client_name}.xlsx')
    else:
        workbook.save(f'{client_name} {file}.xlsx')

    diff = ceil(time.time() - start)
    minutes = floor(diff / 60)
    seconds = (diff % 60)
    secondsString = str(seconds).zfill(2)
    personsString = "Person wurde" if len(people) == 1 else "Personen wurden"
    print(f"[INFO] {len(people)} {personsString} in {minutes}:{secondsString} extrahiert.")

if __name__ == '__main__':
    # Use function to be able to return on errors (`exit()` causes problems when converted to .exe)
    __main()