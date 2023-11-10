import sys
import colorama
import datetime
import logging
import pytz

from typing import Mapping, Union


# Im using two different formatters because of some quirks with logging formatters
# I tried manually setting the self._fmt attribute then ran super().format()
# but it did not seem to keep the modified format so I ended up spliting them
class CentralTimeFormatter(logging.Formatter):
    """Formats the current time in US/Central to an ISO format"""

    def converter(self, timestamp):
        dt = datetime.datetime.fromtimestamp(timestamp)
        tzinfo = pytz.timezone("US/Central")
        return tzinfo.localize(dt)

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            try:
                s = dt.isoformat(timespec="milliseconds")
            except TypeError:
                s = dt.isoformat()

        return s


class ColorFormatter(logging.Formatter):
    """
    Formats the message to use colors using colorama.
    Also uses the CentralTimeFormatter to format the time
    """

    def __init__(
        self,
        fmt=None,
        datefmt=None,
        style="%",
        validate: bool = True,
    ) -> None:
        self._level_colors = {
            logging.DEBUG: colorama.Fore.GREEN,
            logging.INFO: colorama.Fore.BLUE,
            logging.WARN: colorama.Fore.YELLOW,
            logging.ERROR: colorama.Fore.RED,
            logging.CRITICAL: colorama.Fore.RED,
        }
        super().__init__(fmt, datefmt, style, validate)

    def format(self, record: logging.LogRecord) -> str:
        f = (
            colorama.Style.RESET_ALL
            + f"%(name)s:%(asctime)s - {colorama.Style.DIM}{self._level_colors.get(record.levelno)}%(levelname)s"
            + f"- {colorama.Style.BRIGHT}%(message)s"
            + colorama.Style.RESET_ALL
        )

        temp_f = CentralTimeFormatter(f, self.datefmt)

        return temp_f.format(record)


def get_logger(name, bot_level) -> logging.Logger:
    log_level = logging.DEBUG
    if bot_level == "PROD":
        log_level = logging.INFO

    jl = logging.getLogger(name)
    jl.setLevel(log_level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(get_formatter())
    jl.addHandler(handler)

    return jl


def get_formatter() -> logging.Formatter:
    return ColorFormatter(datefmt="%Y/%m/%d - %H:%M:%S:%Z")
