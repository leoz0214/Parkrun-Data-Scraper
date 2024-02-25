"""
Main module of the program - this consists of the GUI and
various input and output screens.
"""
import tkinter as tk
from ctypes import windll
from tkinter import ttk

import auto


windll.shcore.SetProcessDpiAwareness(1)
TITLE = "Parkrun Data Scraper"


class ParkrunScraper(tk.Tk):
    """Parkrun data collection program GUI."""

    def __init__(self) -> None:
        super().__init__()
        self.title(TITLE)
    
        self.notebook = ttk.Notebook(self)
        self.automatic_scraper = auto.AutomaticScraper(self.notebook)
        self.manual_scraper = ManualScraper(self.notebook)
        self.automatic_scraper.pack(padx=10, pady=10)
        self.manual_scraper.pack(padx=10, pady=10)

        self.notebook.add(self.automatic_scraper, text="URL Input")
        self.notebook.add(self.manual_scraper, text="File Input")
        self.notebook.pack(padx=10, pady=10)


class ManualScraper(tk.Frame):
    """
    Manual data collection - must download HTML source from browser
    and input the file path to collect the data.
    """

    def __init__(self, master: ttk.Notebook) -> None:
        super().__init__(master)


def main() -> None:
    """Main procedure of the program."""
    parkrun_scraper = ParkrunScraper()
    parkrun_scraper.mainloop()


if __name__ == "__main__":
    main()
