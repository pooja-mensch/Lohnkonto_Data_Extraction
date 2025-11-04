# This is its own file due to circularity errors
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .classes import MetaData

__current_meta: MetaData | None = None
__pages = None
__current_page = 0

def get_current_meta() -> MetaData:
    global __current_meta
    return __current_meta

def set_current_meta(meta: MetaData):
    global __current_meta
    __current_meta = meta

def get_current_page() -> int:
    global __current_page
    return __current_page

def set_current_page(page: int):
    global __current_page
    __current_page = page

def get_pages():
    global __pages
    return __pages

def set_pages(pages):
    global __pages
    __pages = pages