from typing import Callable, Any

from pypdf import PageObject

lines = []

def __visitor(text: str, um, tm, font_dict, font_size):
    global lines
    lines.append([text, um, tm, font_dict, font_size])

def visit_page(page: PageObject, visitor: Callable[[Any, Any, Any, Any, Any], None]):
    global lines
    lines = []
    page.extract_text(visitor_text=__visitor)
    for line in reversed(sorted(lines, key=lambda x: x[1][5] + x[2][5])):
        visitor(line[0], line[1], line[2], line[3], line[4])