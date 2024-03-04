"""Automatic collection of data given the event URL, using selenium."""
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait as Wait
from selenium.common.exceptions import WebDriverException

from utils import RED, GREEN


MAX_URL_INPUT_LENGTH = 128
LATEST_RESULTS_URL_FORMAT = "https://www.{domain}/{name}/results/eventhistory/"
TIMEOUT = 15
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"


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
        raise ValueError("Invalid URL")
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
        self.cancelled = False
        self.exception = None

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
        self.start_button.config(text="Cancel", command=self.cancel)
        
        threading.Thread(target=self.process, daemon=True).start()
    
    def process(self) -> None:
        """
        Proceeds to scrape the data using selenium in a
        thread to maintain UI responsiveness.
        """
        source = None
        try:
            options = ChromeOptions()
            options.add_argument("--headless=new")
            # Spoof user agent to avoid instant bot detection.
            options.add_argument(f"user-agent={USER_AGENT}")
            # Just to be safe, disguise bot further.
            options.add_experimental_option("useAutomationExtension", False)
            options.add_experimental_option(
                "excludeSwitches", ["enable-automation"])
            options.add_argument(
                "--disable-blink-features=AutomationControlled")
            url = parse_url(self.url)
            with Chrome(options=options) as driver:
                if self.cancelled:
                    raise Exception
                driver.get(url)
                if self.cancelled:
                    raise Exception
                Wait(driver, TIMEOUT).until(
                    EC.presence_of_element_located((By.ID, "primary")))
                if self.cancelled:
                    raise Exception
                source = driver.page_source
        except WebDriverException:
            self.exception = RuntimeError(
                "Summary table failed to load - "
                "check your Internet connection.\n"
                "Otherwise, perhaps the bot has been detected.")
        except Exception as e:
            self.exception = e
        self.stop()
        if source is not None:
            self.master.master.process_html(source)

    def cancel(self) -> None:
        """Cancels the data collection."""
        self.feedback_label.config(text="Cancelling...")
        self.cancelled = True
    
    def stop(self) -> None:
        """Data collection cancelled/finished, or error occurred."""
        if not self.cancelled:
            if self.exception is not None:
                messagebox.showerror(
                    "Error",
                    f"Unfortunately, an error has occurred: {self.exception}")
        self.cancelled = False
        self.exception = None
        for tab in self.master.tabs():
            self.master.tab(tab, state="normal")
        self.url_entry.config(state="normal")
        self.validate_url()
        self.start_button.config(text="Start", command=self.start)

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
