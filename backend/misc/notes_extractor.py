from pypdf import PageObject

from misc.data_holder import get_current_meta

NOTES = ["Entgeltersatzleistungen", "Elternzeit"]

def __notes_visitor(text: str, um, tm, font_dict, font_size):
    for NOTE in NOTES:
        if NOTE in text:
            get_current_meta().notes.append(NOTE)

def detect_notes(page: PageObject):
    page.extract_text(visitor_text=__notes_visitor)