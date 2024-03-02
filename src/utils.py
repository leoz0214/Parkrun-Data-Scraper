"""General utilities shared across the program, including constants."""


RED = "red"
GREEN = "green"


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
