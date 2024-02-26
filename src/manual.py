"""
Manual HTML file input instead of relying on selenium automation -
this completely circumvents anti-bot mechanisms.
"""
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk


class ManualScraper(tk.Frame):
    """
    Manual data collection - must download HTML source from browser
    and input the file path to collect the data.
    """

    def __init__(self, master: ttk.Notebook) -> None:
        super().__init__(master)
        self.info_label = tk.Label(
            self, text=(
                "In case the automated method does not work, "
                "this is the alternative method.\n"
                "1. Navigate to the event history page for your chosen event "
                "e.g. https://www.parkrun.org.uk/bushy/results/eventhistory/\n"
                "2. Right click on the page and press 'Save As'.\n"
                "3. When the file dialog appears, set the Save as type to "
                "'Web Page, Complete', and press 'Save'.\n"
                "4. Ignore/delete the downloaded folder, but input the main "
                "HTML file into the program using the button below."),
            wraplength=1000)
        self.select_button = ttk.Button(
            self, text="Select File", command=self.select)
        
        self.info_label.pack(padx=5, pady=5)
        self.select_button.pack(padx=5, pady=5)
    
    def select(self) -> None:
        """Allows the user to select the HTML file."""
        try:
            with filedialog.askopenfile(
                defaultextension=".html", filetypes=(("HTML", ".html"),),
                title="Select HTML file"
            ) as f:
                source = f.read()
            self.master.master.process_html(source)
        except Exception as e:
            messagebox.showerror(
                "Error", f"Unfortunately, an error occurred: {e}")
