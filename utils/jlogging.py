import colorama
import datetime

def log(name, log):
    print(colorama.Style.RESET_ALL + colorama.Fore.BLUE + f"{name}" + colorama.Fore.MAGENTA + f":{log}" + colorama.Style.RESET_ALL)


def time_log(name, log):
    print(colorama.Style.RESET_ALL + colorama.Fore.BLUE + f"{name}" + colorama.Fore.GREEN +
            f"{datetime.datetime.now()}" + colorama.Fore.MAGENTA + f":{log}" + colorama.Style.RESET_ALL)


def error(name, log):
    print(colorama.Fore.RED + f"ERROR:{name}:{log}" + colorama.Style.RESET_ALL)


def warning(name, log):
    print(colorama.Fore.YELLOW + f"WARNING:{name}:{log}" + colorama.Style.RESET_ALL)