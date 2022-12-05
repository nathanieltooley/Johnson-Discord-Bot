import colorama
import datetime

def log(name, log):
    print(colorama.Style.RESET_ALL + colorama.Fore.BLUE + f"{name}" + colorama.Fore.MAGENTA + f":{log}")


def time_log(name, log):
    print(colorama.Style.RESET_ALL + colorama.Fore.BLUE + f"{name}" + colorama.Fore.GREEN +
            f"{datetime.datetime.now()}" + colorama.Fore.MAGENTA + f":{log}")


def error(name, log):
    print(colorama.Fore.RED + f"ERROR:{name}:{log}")


def warning(name, log):
    print(colorama.Fore.YELLOW + f"WARNING:{name}:{log}")