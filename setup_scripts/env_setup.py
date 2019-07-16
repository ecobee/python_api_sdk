"""Setup Script to configure the enviornment for the Python API SDK."""

import os


def setup():

    print_mode = False
    HOME_DIR = os.path.expanduser("~")
    EBAPI_DIR = os.path.join(HOME_DIR, ".ebapi")

    if not os.path.exists(EBAPI_DIR):
        os.mkdir(EBAPI_DIR)

    api_key = input("Enter you Ecobee Api Application Key: ")

    evs = {
        "EBAPI_USER_TOKENS_FILE": os.path.join(EBAPI_DIR, "tstat.csv"),
        "EBAPI_USER_TSTAT_FILE": os.path.join(EBAPI_DIR, "user.csv"),
        "ECOBEE_APPLICATION_KEY": api_key
    }

    lines = ["#Created by EBAPI Setup stript\n"]
    lines.extend([format_ev(key, val) for key, val in evs.items()])

    prefrences_file = os.path.join(EBAPI_DIR, "prefrences.sh")

    for line in lines:
        print_or_record(prefrences_file, line, print_mode)

    lines = [
        "#Added by the EBAPI setup script\n",
        "source {}\n".format(prefrences_file)
    ]

    bash_profile = os.path.join(HOME_DIR, ".bash_profile")
    for line in lines:
        print_or_record(bash_profile, line, print_mode)


def print_or_record(save_file, string, print_mode):
    if print_mode:
        print("would write {} to {}".format(string, save_file))
    else:
        with open(save_file, 'a') as out_file:
            out_file.write(string)


def format_ev(key, value):
    return 'export {}="{}"\n'.format(key, value)


def input_path(message, default=None):
    while True:
        path = input(message)
        if path == "" and default is not None:
            print("Using default.")
            return path
        elif os.path.exists(path):
            return path
        else:
            print("Error supplied path does not exist please try again.")


if __name__ == "__main__":
    setup()
