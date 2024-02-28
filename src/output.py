"""Module to process HTML data and output it on screen."""
import datetime as dt
import statistics
import tkinter as tk
from collections import Counter
from dataclasses import dataclass
from tkinter import ttk

import lxml
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
    first_male: FirstPlace | None
    first_female: FirstPlace | None


@dataclass
class Data:
    """Summary data for a particular parkrun event."""
    title: str
    mean_finishers: float
    median_finishers: int
    mean_volunteers: float
    median_volunteers: int
    male_record: FirstPlace
    female_record: FirstPlace
    mean_first_male_seconds: int
    mean_first_female_seconds: int
    top_male_winners: list[TopWinner]
    top_female_winners: list[TopWinner]
    cancellation_rate: float
    event_count: int
    finishes: int
    finishers: int
    mean_finishes: float
    volunteers: int
    personal_bests: int
    mean_finish_seconds: int
    groups: int
    email: str
    events: list[EventData]


MOST_FREQUENT_WINNERS_COUNT = 3
ISO_SATURDAY = 6


def mmss_to_seconds(time_: str) -> int:
    """Converts finish time MMSS to seconds."""
    return int(time_[:2]) * 60 + int(time_[2:])


def hh_mm_ss_to_seconds(time_: str) -> int:
    """Converts HH:MM:SS into seconds."""
    hours, minutes, seconds = map(int, time_.split(":"))
    return hours * 3600 + minutes * 60 + seconds


def seconds_to_mmss(seconds: int) -> str:
    """Converts seconds to MM:SS format."""
    minutes, seconds = divmod(seconds, 60)
    return f"{str(minutes).zfill(2)}:{str(seconds).zfill(2)}"


def get_averages(counts: list[int]) -> tuple[float, int]:
    """Returns mean and median of counts (median rounded to integer)."""
    mean = statistics.mean(counts)
    median = round(statistics.median(counts))
    return mean, median


def get_first_finishers_data(
    first_finishers: list[FirstPlace]
) -> tuple[FirstPlace, int, list[TopWinner]]:
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
    return fastest, round(mean_seconds), top_winners


def get_cancellation_rate(dates: list[dt.date]) -> float:
    """
    Returns the cancellation rate (based on number of missing weeks between
    the first and last dates). IGNORES CHRISTMAS/NEW YEAR SPECIAL RUNS,
    only consider Saturday runs.
    """
    saturday_events = [
        date for date in dates if date.isoweekday() == ISO_SATURDAY]
    time_between = max(saturday_events) - min(saturday_events)
    expected_events = time_between.days // 7 + 1
    actual_events = len(saturday_events)
    return 1 - actual_events / expected_events


def get_stat_value(soup: BeautifulSoup, label: str) -> str:
    """Returns statistic value on website given label text."""
    for stat in soup.find_all(class_="aStat"):
        if label in stat.text:
            return stat.find("span").text


def parse_source(source: str) -> Data:
    """
    Returns historical data from HTML past results page.
    No parkrun has many events, performance not crucial.
    """
    try:
        soup = BeautifulSoup(source, "lxml")
    except Exception:
        # Fall back to slower html.parser if LXML unavailable.
        soup = BeautifulSoup(source, "html.parser")
    table = soup.find("table", class_="Results-table").find("tbody")
    events_data = []
    for row in table.find_all("tr"):
        number = int(row["data-parkrun"])
        # DD/MM/YYYY -> Year, Month, Day
        date = dt.date(*reversed(tuple(map(int, row["data-date"].split("/")))))
        finishers = int(row["data-finishers"])
        volunteers = int(row["data-volunteers"])

        first_male_url, first_female_url, *_ = (
            a["href"] for a in row.find_all(
                "a", href=lambda href: href and "athlete" in href))
        first_male_name = row["data-male"]
        if first_male_name:
            first_male_time = mmss_to_seconds(row["data-maletime"])
            first_male_id = int(first_male_url.split("=")[1])
            first_male = FirstPlace(
                first_male_id, first_male_name, first_male_time)
        else:
            first_male = None
        first_female_name = row["data-female"]
        if first_female_name:
            first_female_time = mmss_to_seconds(row["data-femaletime"])
            first_female_id = int(first_female_url.split("=")[1])
            first_female = FirstPlace(
                first_female_id, first_female_name, first_female_time)
        else:
            first_female = None
        record = EventData(
            number, date, finishers, volunteers, first_male, first_female)
        events_data.append(record)

    finisher_counts = [event.finishers for event in events_data]
    mean_finishers, median_finishers = get_averages(finisher_counts)
    volunteer_counts = [event.volunteers for event in events_data]
    mean_volunteers, median_volunteers = get_averages(volunteer_counts)

    first_male_finishers = [
        event.first_male for event in events_data
        if event.first_male is not None]
    male_record, mean_first_male_seconds, top_male_winners = (
        get_first_finishers_data(first_male_finishers))
    first_female_finishers = [
        event.first_female for event in events_data
        if event.first_female is not None]
    female_record, mean_first_female_seconds, top_female_winners = (
        get_first_finishers_data(first_female_finishers))
    
    dates = [event.date for event in events_data]
    cancellation_rate = get_cancellation_rate(dates)

    event_count = len(events_data)
    title = soup.find("h1").text.removesuffix(" parkrun Event History")
    finishes = int(get_stat_value(soup, "Finishes:").replace(",", ""))
    finishers = int(get_stat_value(soup, "Finishers:").replace(",", ""))
    mean_finishes = finishes / finishers
    volunteers = int(get_stat_value(soup, "Volunteers:").replace(",", ""))
    personal_bests = int(get_stat_value(soup, "PBs:").replace(",", ""))
    mean_finish_seconds = hh_mm_ss_to_seconds(
        get_stat_value(soup, "Average finish time:"))
    groups = int(get_stat_value(soup, "Groups:").replace(",", ""))
    email = soup.find("a", href=lambda href: href and "mailto" in href).text
    # Bundles all data obtained in this function into a data class.
    return Data(
        title, mean_finishers, median_finishers, mean_volunteers,
        median_volunteers, male_record, female_record, mean_first_male_seconds,
        mean_first_female_seconds, top_male_winners, top_female_winners,
        cancellation_rate, event_count, finishes, finishers, mean_finishes,
        volunteers, personal_bests, mean_finish_seconds, groups, email,
        events_data)


class OutputScreen(tk.Frame):
    """Data output screen, including exportation facilities."""

    def __init__(self, master: ttk.Notebook) -> None:
        super().__init__(master)
        self.no_data_label = tk.Label(
            self, text="No data yet!\nInput a URL or file to get started.")
        self.title_label = tk.Label(self, anchor="center")
        self.mean_finishers_label = tk.Label(self, width=25)
        self.median_finishers_label = tk.Label(self, width=25)
        self.mean_volunteers_label = tk.Label(self, width=25)
        self.median_volunteers_label = tk.Label(self, width=25)
        self.male_record_label = tk.Label(self, width=50)
        self.female_record_label = tk.Label(self, width=50)
        self.male_mean_first_time_label = tk.Label(self, width=25)
        self.female_mean_first_time_label = tk.Label(self, width=25)
        self.male_top_winners_frame = TopWinnersFrame(self, "male")
        self.female_top_winners_frame = TopWinnersFrame(self, "female")
        self.no_data_label.pack(padx=25, pady=25)
    
    def process(self, source: str) -> None:
        """
        Process the HTML data, obtaining relevant data
        and displaying it appropriately.
        """
        data = parse_source(source)
        for widget in self.children.values():
            widget.pack_forget()
            widget.grid_forget()
        self.title_label.config(text=f"{data.title} Parkrun - Statistics")
        self.mean_finishers_label.config(
            text=f"Mean finishers: {data.mean_finishers:.1f}")
        self.median_finishers_label.config(
            text=f"Median finishers: {data.median_finishers}")
        self.mean_volunteers_label.config(
            text=f"Mean volunteers: {data.mean_volunteers:.1f}")
        self.median_volunteers_label.config(
            text=f"Median volunteers: {data.median_volunteers}")
        self.male_record_label.config(
            text=(
                f"Male course record: {data.male_record.name} | "
                f"A{data.male_record.athlete_id} | "
                f"{seconds_to_mmss(data.male_record.seconds)}"))
        self.female_record_label.config(
            text=(
                f"Female course record: {data.female_record.name} | "
                f"A{data.female_record.athlete_id} | "
                f"{seconds_to_mmss(data.female_record.seconds)}"))
        self.male_mean_first_time_label.config(
            text=(
                "Mean male 1st time: "
                f"{seconds_to_mmss(data.mean_first_male_seconds)}"))
        self.female_mean_first_time_label.config(
            text=(
                "Mean female 1st time: "
                f"{seconds_to_mmss(data.mean_first_female_seconds)}"))
        self.male_top_winners_frame.set(data.top_male_winners)
        self.female_top_winners_frame.set(data.top_female_winners)

        self.title_label.grid(row=0, column=0, columnspan=2, padx=5, pady=3)
        self.mean_finishers_label.grid(row=1, column=0, padx=5, pady=3)
        self.median_finishers_label.grid(row=1, column=1, padx=5, pady=3)
        self.mean_volunteers_label.grid(row=2, column=0, padx=5, pady=3)
        self.median_volunteers_label.grid(row=2, column=1, padx=5, pady=3)
        self.male_record_label.grid(
            row=3, column=0, columnspan=2, padx=5, pady=3)
        self.female_record_label.grid(
            row=4, column=0, columnspan=2, padx=5, pady=3)
        self.male_mean_first_time_label.grid(row=5, column=0, padx=5, pady=3)
        self.female_mean_first_time_label.grid(row=5, column=1, padx=5, pady=3)
        self.male_top_winners_frame.grid(row=6, column=0, padx=5, pady=(15, 3))
        self.female_top_winners_frame.grid(
            row=6, column=1, padx=5, pady=(15, 3))


class TopWinnersFrame(tk.Frame):
    """
    Frame for displaying information on the
    most frequent winners of a particular Parkrun.
    """

    def __init__(self, master: OutputScreen, gender: str) -> None:
        super().__init__(master)
        self.label = tk.Label(self, text=f"Most frequent {gender} winners:")
        self.info_label = tk.Label(self)
        self.label.pack()
        self.info_label.pack()
    
    def set(self, top_winners: list[TopWinner]) -> None:
        """Updates the info label given the top winners."""
        text = "\n".join(
            f"{n}. {winner.name} | A{winner.athlete_id} | x{winner.wins}"
            for n, winner in enumerate(top_winners, 1))
        self.info_label.config(text=text)
    