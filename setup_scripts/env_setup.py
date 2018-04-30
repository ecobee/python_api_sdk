"""Setup Script to configure the enviornment for the Python API SDK."""

import os



class Setup:
    
    def __init__(self, print_mode):
        self.print_mode = print_mode
        self.pref_file = self.get_preferences_location()

    def get_preferences_location(self)
        default_directory = os.path.expanduser("~")
        preferences_file_name = ".ebapi_preferences"
        default_save_file = os.path.join(home, preferences_file_name)
        save_dir = input_path("Where should we save your preferences?\n" \
                              "Enter nothing to use default: {}".format(default_save_file))
        if save_dir == "":
            return default_save_file
        else:
            return os.path.join(save_dir, preferences_file_name)

    def get_api_key(self):
        api_key = input("Enter you Ecobee Api Application Key: ")
        self.store_key_value(self.pref_file, "ECOBEE_APPLICATION_KEY", api_key)

    def get_local_creds_directory(self):
        path = input_path("Where should we save our ")

    def input_path(self, message, default=None):
        while True:
            path = input(message)
            if path == "" and default is not None:
                print("Using default.")
                return path
            elif os.path.exists(path):
                return path
            else:
                print("Error supplied path does not exist please try again.")
    def store_key_value(self, save_file, key, value):
        line = 'export {}="{}"\n'.format(key, value)
        try:
            self.lines[save_file].append(
        except KeyError:
            self.lines[save_file] = [line]

    def print_or_record(self, save_file, string):
        if self.print_mode:
            print("would write {} to {}".format(string, save_file))
        else:
            with open(save_file, 'w') as out_file:
                outfile.write(string)
            
