"""
Module for handling exporting data to various file types:
CSV, XLSX, DOCX and PDF.
"""
import csv
import io

import docx
import docx.document
import openpyxl
from docx.shared import Inches, Pt
from matplotlib import pyplot as plt
from openpyxl.styles.fonts import Font

import output
from utils import seconds_to_mmss


# Tabular output columns
TABLE_COLUMNS = (
    "Event Number", "Date", "Finishers", "Volunteers",
    "Male 1st Name", "Male 1st Athlete ID", "Male 1st Seconds",
    "Female 1st Name", "Female 1st Athlete ID", "Female 1st Seconds"
)
MAX_SHEET_NAME_LENGTH = 31
GRAPH_WIDTH = Inches(5)
GRAPH_HEIGHT = Inches(3)
TITLE_SIZE = Pt(32)
HEADING_1_SIZE = Pt(24)
TEXT_SIZE = Pt(16)


def get_event_records(events: list["output.EventData"]) -> list[list]:
    """Converts event data objects into records to be written to CSV/XLSX."""
    records = []
    for event in events:
        record = [event.number, event.date, event.finishers, event.volunteers]
        for first in (event.first_male, event.first_female):
            if first is not None:
                record.extend((first.name, first.athlete_id, first.seconds))
            else:
                record.extend((None, None, None))
        records.append(record)
    return records


def save_csv(events: list["output.EventData"], file_path: str) -> None:
    """Saves event data to CSV."""
    records = get_event_records(events)
    with open(file_path, "w", encoding="utf8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(TABLE_COLUMNS)
        writer.writerows(records)


def save_xlsx(data: "output.Data", file_path: str) -> None:
    """Saves event data to XLSX."""
    records = get_event_records(data.events)
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = f"{data.title} Parkrun"[:MAX_SHEET_NAME_LENGTH]
    sheet.append(TABLE_COLUMNS)
    # Make headings bold.
    for column in range(1, len(TABLE_COLUMNS) + 1):
        sheet.cell(row=1, column=column).font = Font(bold=True)
    for record in records:
        sheet.append(record)
    workbook.save(file_path)


def add_graph(
    document: docx.document.Document, data: "output.Data",
    label: str, attribute: str
) -> None:
    """Adds graph for given metric to given document."""
    plt.figure()
    output.plot_graph(data, label, attribute)
    with io.BytesIO() as graph_bytes:
        plt.savefig(graph_bytes)
        graph_bytes.seek(0)
        document.add_picture(graph_bytes, GRAPH_WIDTH, GRAPH_HEIGHT)
    plt.close()


def generate_docx(data: "output.Data") -> docx.document.Document:
    """Generates and returns a DOCX report ready to be saved."""
    document: docx.document.Document = docx.Document()
    document.styles["Title"].font.size = TITLE_SIZE
    document.styles["Heading 1"].font.size = HEADING_1_SIZE
    document.styles["Normal"].font.size = TEXT_SIZE
    document.add_heading(f"{data.title} Parkrun - Statistics", 0)
    document.add_heading("Event Popularity", 1)
    popularity_points = (
        f"Mean finishers: {data.mean_finishers:.1f}",
        f"Median finishers: {data.median_finishers}",
        f"Mean volunteers: {data.mean_volunteers:.1f}",
        f"Median volunteers: {data.median_volunteers}")
    for point in popularity_points:
        document.add_paragraph(point, style="List Bullet")
    add_graph(document, data, "Finishers", "finishers")
    add_graph(document, data, "Volunteers", "volunteers")

    document.add_heading("Competitive", 1)
    document.add_paragraph(
        f"The male course record is held by {data.male_record.name} "
        f"(A{data.male_record.athlete_id}), with a time of "
        f"{seconds_to_mmss(data.male_record.seconds)}.")
    document.add_paragraph(
        f"The female course record is held by {data.female_record.name} "
        f"(A{data.female_record.athlete_id}), with a time of "
        f"{seconds_to_mmss(data.female_record.seconds)}.")
    document.add_paragraph(
        f"The mean male 1st place time is "
        f"{seconds_to_mmss(data.mean_first_male_seconds)}.")
    document.add_paragraph(
        f"The mean female 1st place time is: "
        f"{seconds_to_mmss(data.mean_first_female_seconds)}.")
    
    # TODO - table of most frequent winners (including up to 10)
    # need to implement columns and add data.

    return document


def save_docx(data: "output.Data", file_path: str) -> None:
    """Saves a DOCX report on event data."""
    document = generate_docx(data)
    document.save(file_path)


def save_pdf(data: "output.Data", file_path: str) -> None:
    """Saves a PDF report on event data."""
    # TODO - same as docx except extra step docx->pdf.
