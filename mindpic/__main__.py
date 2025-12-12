# File: mindpic/__main__.py
# -*- coding: utf-8 -*-


from __future__ import annotations

import tkinter as tk

from .app import MindPicApp
from . import settings


def main() -> None:
    root = tk.Tk()
    # optional: WM_CLASS / AppUserModelID (Windows) könnte man hier setzen, falls nötig
    _app = MindPicApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
