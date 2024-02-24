# Parkrun Data Scraper

Parkrun is a weekly free timed 5k event mostly based in the UK and Ireland,
but also has various events worldwide.

Previously, various statistics were available to see, providing insights
on events such as course records and event popularity. Much of this
has been removed on the website to apparently promote inclusivity of Parkrun.

Nonetheless, many of the statistics are still deducible by processing
the summary table of past events. This project aims to take the HTML of
that page, parse it, and generate detailed statistics and graphs accordingly.

Also, Parkrun has anti-bot measures in place which this program will
circumvent to a reasonable degree. In order to minimise the burden,
a semi-manual procedure can be followed which does not involve programmatic requests - 
virtually immune to anti-bot mechanisms.

Feature overview (planned to implement):
- Automatic downloading of HTML using Selenium (input URL).
- Manual input of HTML page (manually download in browser).
- Statistics screen (parsed from HTML)
- Graphs can be viewed
- Export report to DOCX/PDF
- Export data to CSV/XLSX

Target time to complete: 1 week and a bit.