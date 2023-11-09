import sys
import colorama
import datetime
import logging
import pytz


class JohnsonFormatter(logging.Formatter):
    def converter(self, timestamp):
        dt = datetime.datetime.fromtimestamp(timestamp)
        tzinfo = pytz.timezone("US/Central")
        return tzinfo.localize(dt)


def log(name, log):
    print(
        colorama.Style.RESET_ALL
        + colorama.Fore.BLUE
        + f"{name}"
        + colorama.Fore.MAGENTA
        + f":{log}"
        + colorama.Style.RESET_ALL
    )


def time_log(name, log):
    print(
        colorama.Style.RESET_ALL
        + colorama.Fore.BLUE
        + f"{name}"
        + colorama.Fore.GREEN
        + f"{datetime.datetime.now()}"
        + colorama.Fore.MAGENTA
        + f":{log}"
        + colorama.Style.RESET_ALL
    )


def error(name, log):
    print(colorama.Fore.RED + f"ERROR:{name}:{log}" + colorama.Style.RESET_ALL)


def warning(name, log):
    print(colorama.Fore.YELLOW + f"WARNING:{name}:{log}" + colorama.Style.RESET_ALL)


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
    return JohnsonFormatter("%(asctime)s - %(levelname)s - %(message)s")
