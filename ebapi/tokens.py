import pandas as pd
import os
import logging
import requests


logger = logging.getLogger(__name__)

class FileTokens():
    user_ev = "EBAPI_USER_TOKENS_FILE"
    tstat_ev = "EBAPI_USER_TSTAT_FILE"
    missing_env_vars = "Enviornment Variables EBAPI_USER_TOKENS_FILE and EBAPI_USER_TSTAT_FILE not Found"
    missing_env_var = "Enviornment Variable {} Not Found"
    unknown_tstat = "Unknown Thermostat ID: {}"
    user_cols = ["user_id", "access_token", "refresh_token"]
    tstat_cols = ["tstat_id", "user_id"]

    def __init__(self, verbose=False):
        self.load_env_vars_if_valid()
        self.load_csvs()

    def load_env_vars_if_valid(self):
        not_found = self.get_missing_evs()
        if not_found != []:
            self.raise_env_exception(not_found)
        else:
            self.load_evs()

    def get_missing_evs(self):
        not_found = []
        for name in [self.user_ev, self.tstat_ev]:
            try:
                os.environ[name]
            except KeyError:
                not_found.append(name)
        return not_found

    def raise_env_exception(self, not_found):
        if len(not_found) == 2:
            raise EnvironmentError(self.missing_env_vars)
        else:
            err_msg = self.missing_env_var.format(not_found[0])
            raise EnvironmentError(err_msg)

    def load_evs(self):
        self.user_file = os.environ[self.user_ev]
        self.tstat_file = os.environ[self.tstat_ev]

    def load_csvs(self):
        missing_files = self.get_missing_files()
        if missing_files == []:
            self.load_user_file()
            self.load_tstat_file()
        elif len(missing_files) == 1:
            self.raise_file_missing_error(missing_files)
        else:
            self.init_new_files()

    def load_user_file(self):
        index_name = 'user_id'
        dtype = {'user_id': str, 'access_token': str, 'refresh_token': str}
        self.user = pd.read_csv(self.user_file, dtype=dtype)
        self.user.set_index(index_name, inplace=True)

    def load_tstat_file(self):
        index_name = 'tstat_id'
        dtype = {'tstat_id': str, 'user_id': str}
        self.tstat = pd.read_csv(self.tstat_file, dtype=dtype)
        self.tstat.set_index(index_name, inplace=True)

    def get_missing_files(self):
        missing_files = []
        for fname in [self.user_file, self.tstat_file]:
            if not os.path.exists(fname):
                missing_files.append(fname)
        return missing_files

    def raise_file_missing_error(self, missing_files):
        err_msg = "Data Corrupted {} Missing.".format(missing_files[0])
        raise EnvironmentError(err_msg)

    def init_new_files(self):
        self.user = pd.DataFrame(columns=self.user_cols)
        self.user.set_index("user_id", inplace=True)
        self.tstat = pd.DataFrame(columns=self.tstat_cols)
        self.tstat.set_index("tstat_id", inplace=True)
        self.save_files()

    def save_files(self):
        self.save_user_file()
        self.save_tstat_file()

    def save_user_file(self):
        self.user.to_csv(self.user_file)

    def save_tstat_file(self):
        self.tstat.to_csv(self.tstat_file)

    def refresh(self):
        for idx, row in self.user.iterrows():
            ref = row["refresh_token"]
            try:
                self.user.loc[idx] = self.refresh_token(ref)
            except Exception:
                pass
            finally:
                self.save_user_file()

    def get_next_user_id(self):
        user_id = len(self.user) + 1
        logger.info("Generating New User ID: {}".format(user_id))
        return user_id

    def delete(self, tstat_id):
        if not self.has_tstat(tstat_id):
            raise KeyError(self.unknown_tstat.format(tstat_id))

        user_id = self.tstat.loc[tstat_id, "user_id"]
        self.drop_tstat(tstat_id)

        if user_id not in self.tstat.user_id.unique():
            self.drop_user(user_id)
        self.save_files()

    def has_tstat(self, tstat_id):
        return tstat_id in self.tstat.index

    def has_user(self, user_id):
        return self.user_id in self.user.index

    def drop_tstat(self, tstat_id):
        logger.info("Droping Tstat {}".format(tstat_id))
        self.tstat.drop(tstat_id, inplace=True)
        self.save_tstat_file()

    def drop_user(self, user_id):
        logger.info("Droping User {}".format(user_id))
        self.user.drop(user_id, inplace=True)
        self.save_user_file()

    def insert(self, user_id, tstat_id, acc, ref):
        self.insert_user(user_id, acc, ref)
        self.insert_tstat(user_id, tstat_id)

    def insert_user(self, user_id, acc, ref):
        if user_id in self.user.index:
            raise RuntimeError("Attempt to overwrite user {}".format(user_id))
        self.user.loc[user_id] = [acc, ref]
        self.save_user_file()

    def insert_tstat(self, user_id, tstat_id):
        if tstat_id in self.tstat.index:
            msg = "ID: {} Already entered for User: {}".format(tstat_id, user_id)
            raise ResourceWarning(msg)

        self.tstat.loc[tstat_id] = user_id
        self.save_tstat_file()

    def get_access_token(self, tstat_id):
        try:
            user_id = self.tstat.loc[tstat_id, "user_id"]
            return self.lookup_access_token(user_id)
        except KeyError:
            raise KeyError(self.unknown_tstat.format(tstat_id))

    def lookup_access_token(self, user_id):
        try:
            row_counts = self.user.index.value_counts()
            row_num = row_counts[user_id]
            if row_num > 1:
                raise ValueError("Corrupted State Multiple rows found for User {}".format(user_id))
            return self.user.loc[user_id, "access_token"]
        except KeyError:
            msg = "No tokens found for user {}".format(user_id)
            raise KeyError(msg)

    def display_tokens(self):
        print("Users")
        print(self.user)
        print()
        print("Thermostats")
        print(self.tstat)
        print()

    def refresh_token(self, ref_token, apoi_key):
        """Refreshe the tokens for a single thermostat."""
        logger.info("Original refresh_tokens")

        headers = {"Content-Type": "application/json;charset=UTF-8"}
        url = 'https://api.ecobee.com/token'
        params = {"grant_type": "refresh_token",
                  "code": ref_token,
                  "client_id": api_key}
        r = requests.post(url, params=params, headers=headers)
        jsn = r.json()
        try:
            tokens = (jsn["access_token"], jsn["refresh_token"])
            return tokens
        except KeyError:
            raise RuntimeError("Error parsing Json:\n {}".format(jsn))
