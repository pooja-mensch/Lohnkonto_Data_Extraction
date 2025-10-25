# This is its own file due to circularity errors
__current_meta = None
__pages = None
__current_page = 0

def get_current_meta():
    global __current_meta
    return __current_meta

def set_current_meta(meta):
    global __current_meta
    __current_meta = meta

def get_current_page():
    global __current_page
    return __current_page

def set_current_page(page):
    global __current_page
    __current_page = page

def get_pages():
    global __pages
    return __pages

def set_pages(pages):
    global __pages
    __pages = pages