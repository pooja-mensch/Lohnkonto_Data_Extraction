from enum import Enum

from pypdf import PageObject

from .data_holder import get_current_meta, get_current_page

class MetaData:
    client_name: str = ""
    year: int = 0
    name: str = ""
    surname: str = ""
    weekly_hours: str
    first_start: str
    start: str
    end: str
    notes: list[str]

    def __init__(self, client_name = "", year = 0, name = "", surname = "", weekly_hours = "", first_start = "", start = "", end = "", notes = []):
        self.client_name = client_name
        self.year = year
        self.name = name
        self.surname = surname
        self.weekly_hours = weekly_hours
        self.first_start = first_start
        self.start = start
        self.end = end
        self.notes = notes


class Person:
    meta: MetaData
    months: list[dict[str, str]]

    def __init__(self, meta, months):
        self.meta = meta
        self.months = months

class MetaDetector:
    meta: MetaData

    def _check_length(self, *strings):
        for string in strings:
            if len(string) == 0:
                return False
        return True

    def detect_meta(self, page: PageObject):
        self.meta = MetaData()
        self.reset()

        page.extract_text(visitor_text=self.visitor)

        for key in self.meta.__dict__:
            print(f"{key} = {self.meta.__dict__[key]}")
        if not self._check_length(self.meta.client_name, self.meta.surname, self.meta.name) or self.meta.year == 0:
            return None

        return self.meta

    def reset(self):
        pass

    def visitor(self, text: str, um, tm, font_dict, font_size):
        pass


class DataMode(Enum):
    SET = 0
    ADD = 1
    SUB = 2

class DataExtractor:
    month = -1
    months = [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]

    def set_data(self, key: str, value: str, mode: DataMode):
        value = value.strip().replace(".", "")

        if not key in self.months[self.month]:
            for month in range(self.month, 12):
                if key in self.months[month]:
                    # Correction of previous year
                    for m in range(month, 12):
                        self.months[m].pop(key, None)
                    print(f"[WARNUNG] Für {get_current_meta().name}, {get_current_meta().surname} existieren Nachbearbeitungen für das vorherige Jahr. (Seite {get_current_page() + 1})")
                    break

        if not value.isdigit():
            if mode != DataMode.SET:
                print(f"[ERROR]: not set, but not digit for {get_current_meta().name}, {get_current_meta().surname}")
                exit(2)
            return

        if mode == DataMode.SET:
            self.months[self.month][key] = int(value)
        elif mode == DataMode.ADD:
            self.months[self.month][key] += int(value)
        elif mode == DataMode.SUB:
            self.months[self.month][key] -= int(value)

    def process_page(self, page: PageObject, _start_page: bool):
        pass