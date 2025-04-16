from django.http import HttpRequest
from django.urls import resolve

from SIGC.constants import (
    SIDEBAR_ICONS_SIZE,
    OPTIONS_ICONS_SIZE,
    STATUS,
    HEADER_ICONS_SIZE,
)


def get_icons_size(request: HttpRequest):
    return {
        "sidebar_size": SIDEBAR_ICONS_SIZE,
        "option_size": OPTIONS_ICONS_SIZE,
        "header_size": HEADER_ICONS_SIZE,
    }


def get_task_status(request: HttpRequest):
    return {"task_status": STATUS._display_map}


def get_dynamic_url(request: HttpRequest):
    early_retirement = ""
    contract_termination = ""

    return {}

