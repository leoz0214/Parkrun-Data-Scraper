"""Module to process HTML data and output it on screen."""
import datetime as dt
import statistics
import tkinter as tk
from collections import Counter
from dataclasses import dataclass
from tkinter import ttk

from bs4 import BeautifulSoup


@dataclass
class FirstPlace:
    """Data for a first place finisher."""
    athlete_id: int
    name: str
    seconds: int


@dataclass
class TopWinner:
    """Data for a top winner (one of the most frequent for the event)."""
    athlete_id: int
    name: str
    wins: int


@dataclass
class EventData:
    """Data for a particular row (single event)."""
    number: int
    date: dt.date
    finishers: int
    volunteers: int
    first_male: FirstPlace
    first_female: FirstPlace


@dataclass
class Data:
    """Summary data for a particular parkrun event."""
    title: str
    mean_finishers: float
    median_finishers: int
    mean_volunteers: float
    median_volunteers: int


MOST_FREQUENT_WINNERS_COUNT = 3


def mmss_to_seconds(time_: str) -> int:
    """Converts finish time MMSS to seconds."""
    return int(time_[:2]) * 60 + int(time_[2:])


def get_averages(counts: list[int]) -> tuple[float, int]:
    """Returns mean and median of counts (median rounded to integer)."""
    mean = statistics.mean(counts)
    median = round(statistics.median(counts))
    return mean, median


def get_first_finishers_data(
    first_finishers: list[FirstPlace]
) -> tuple[FirstPlace, float, list[TopWinner]]:
    """
    Returns data on first finishers of a particular gender,
    including course record, mean first time, top N most frequent winners.
    """
    fastest = min(first_finishers, key=lambda finish: finish.seconds)
    mean_seconds = statistics.mean(
        finish.seconds for finish in first_finishers)
    top_first_finishers = Counter(
        (finisher.athlete_id, finisher.name) for finisher in first_finishers
    ).most_common(MOST_FREQUENT_WINNERS_COUNT)
    top_winners = [
        TopWinner(*athlete, wins=count)
        for athlete, count in top_first_finishers]
    return fastest, mean_seconds, top_winners


def parse_source(source: str) -> Data:
    """
    Returns historical data from HTML past results page.
    No parkrun has many events, performance not crucial.
    """
    soup = BeautifulSoup(source, "html.parser")
    title = soup.find("h1").text.removesuffix(" parkrun Event History")
    table = soup.find("table", class_="Results-table").find("tbody")
    events_data = []
    for row in table.find_all("tr"):
        number = int(row["data-parkrun"])
        # DD/MM/YYYY -> Year, Month, Day
        date = dt.date(*reversed(tuple(map(int, row["data-date"].split("/")))))
        finishers = int(row["data-finishers"])
        volunteers = int(row["data-volunteers"])
        first_male_name = row["data-male"]
        first_female_name = row["data-female"]
        first_male_time = mmss_to_seconds(row["data-maletime"])
        first_female_time = mmss_to_seconds(row["data-femaletime"])
        first_male_url, first_female_url, *_ = (
            a["href"] for a in row.find_all(
                "a", href=lambda href: href and "athlete" in href))
        first_male_id = int(first_male_url.split("=")[1])
        first_female_id = int(first_female_url.split("=")[1])
        record = EventData(
            number, date, finishers, volunteers,
            FirstPlace(first_male_id, first_male_name, first_male_time),
            FirstPlace(first_female_id, first_female_name, first_female_time))
        events_data.append(record)

    finisher_counts = [event.finishers for event in events_data]
    mean_finishers, median_finishers = get_averages(finisher_counts)
    volunteer_counts = [event.volunteers for event in events_data]
    mean_volunteers, median_volunteers = get_averages(volunteer_counts)

    first_male_finishers = [event.first_male for event in events_data]
    male_record, mean_male_seconds, top_male_winners = (
        get_first_finishers_data(first_male_finishers))
    first_female_finishers = [event.first_female for event in events_data]
    female_record, femean_male_seconds, top_female_winners = (
        get_first_finishers_data(first_female_finishers))


class OutputScreen(tk.Frame):
    """Data output screen, including exportation facilities."""

    def __init__(self, master: ttk.Notebook) -> None:
        super().__init__(master)
        self.no_data_label = tk.Label(
            self, text="No data yet!\nInput a URL or file to get started.")
        self.no_data_label.pack(padx=25, pady=25)
    
    def process(self, source: str) -> None:
        """
        Process the HTML data, obtaining relevant data
        and displaying it appropriately.
        """
        data = parse_source(source)