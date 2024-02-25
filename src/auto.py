"""Automatic collection of data given the event URL, using selenium."""
import tkinter as tk
from tkinter import ttk

from utils import RED, GREEN


MAX_URL_INPUT_LENGTH = 128
LATEST_RESULTS_URL_FORMAT = "https://www.{domain}/{name}/results/eventhistory/"


def parse_url(url: str) -> str:
    """
    Validates a parkrun event URL, raising an error upon failure.
    If successful, returns corresponding URL to fetch data from.
    """
    # Strip away protocol from URL if present.
    for protocol in ("http://", "https://"):
        if url.startswith(protocol):
            url = url.removeprefix(protocol)
            break
    # Strip away www. if present.
    url = url.removeprefix("www.")
    # Ignore trailing slashes.
    url = url.rstrip("/")
    # Split URL into parts.
    parts = url.split("/")
    # Check parts in either format:
    # domain/parkrun-name or domain/parkrun-name/results/eventhistory
    if len(parts) not in (2, 4):
        raise ValueError("Invalid URL")
    # Basic domain validity check.
    domain = parts[0]
    if (
        not domain.startswith("parkrun")
        or ".." in domain or domain.endswith(".") or not domain.count(".")
        or not domain.replace(".", "").isalpha()
    ):
        raise ValueError("Invalid domain")
    # Basic parkrun name validity check.
    name = parts[1]
    if not name.isalpha():
        raise ValueError("Invalid parkrun name")
    if len(parts) == 4 and (
        parts[2] != "results" or parts[3] != "eventhistory"
    ):
        raise ValueError("Invalid domain")
    return LATEST_RESULTS_URL_FORMAT.format(domain=domain, name=name)


class AutomaticScraper(tk.Frame):
    """
    Automatic data collection - input event URL and 
    wait for selenium window to collect the data.
    """

    def __init__(self, master: ttk.Notebook) -> None:
        super().__init__(master)
        self._url = tk.StringVar()
        self._url.trace_add("write", lambda *_: self.validate_url())
        self.previous_url = ""
        self.info_label = tk.Label(
            self, text=(
                "Provide the URL to the Parkrun event you wish to "
                "scrape data from.\n"
                "An example of a valid URL is: "
                "https://www.parkrun.org.uk/bushy/"), wraplength=1000)
        self.url_entry = ttk.Entry(self, width=64, textvariable=self._url)
        self.feedback_label = tk.Label(self)
        self.start_button = ttk.Button(
            self, text="Start", state="disabled", command=self.start)

        self.info_label.pack(padx=5, pady=5)
        self.url_entry.pack(padx=5, pady=5)
        self.feedback_label.pack(padx=5, anchor="e")
        self.start_button.pack(padx=5, pady=5)

    @property
    def url(self) -> str:
        return self._url.get().strip().lower()

    def start(self) -> None:
        """Starts the automated data collection from the URL."""
        # Disable all other tabs except current tab (avoid thread issues).
        for tab in self.master.tabs():
            if str(type(self).__name__).lower() not in str(tab):
                self.master.tab(tab, state="disabled")
        self.url_entry.config(state="disabled")
        self.feedback_label.config(text="Processing...")
        self.start_button.config(text="Cancel")
        print(parse_url(self.url))

    def validate_url(self) -> None:
        """
        Validates the URL, adjusting the feedback message 
        and start button state accordingly.
        """
        url = self.url
        if len(url) > MAX_URL_INPUT_LENGTH:
            self._url.set(self.previous_url)
            return
        self.previous_url = url
        if not url:
            self.feedback_label.config(text="")
            self.start_button.config(state="disabled")
            return
        try:
            parse_url(url)
        except Exception as e:
            self.feedback_label.config(text=e, fg=RED)
            self.start_button.config(state="disabled")
        else:
            self.feedback_label.config(text="Valid URL", fg=GREEN)
            self.start_button.config(state="normal")
