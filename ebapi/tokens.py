"""This file impliments the FileTokens class.

   The class stores auth and refresh tokens for multiple Ecobee Devices locally
   used to interact with the Ecobee API.
"""

import os
import logging
import requests
import pandas as pd

from ebapi.constants import env_vars


logger = logging.getLogger(__name__)

class Config:
    """This class stores the enviornment variables."""

    def __init__(self):
        """Populate enviornment variables."""

        self.validate_enviornment()

        self.user_file = os.environ[env_vars.EV_USER_TOKEN_FILE]
        self.tstat_file = os.environ[env_vars.EV_USER_TSTAT_FILE]
        self.app_key = os.environ[env_vars.EV_APP_KEY]

    def validate_enviornment(self):
        """Return a list of the the enviornment variables not found."""
       
        missing_evs = [ev for ev in env_vars.REQUIRED_EVS if ev not in os.environ.keys()]

        if missing_evs:
            err_fmt = "Could not find EBAPI enviornment variabel(s): {}"
            err_msg = err_fmt.format(", ".join(missing_evs))
            raise EnvironmentError(err_msg)


class FileTokens:
    """File Storage of access and refresh tokens."""

    def __init__(self, verbose=False):
        """Load enviornment variables and stored files"""
        
        self.unknown_tstat = "Unknown Thermostat ID: {}"

        self.config = Config()

        self._user = None
        self._tstat = None

        self._load_csvs()

    def _load_csvs(self):
        """Load the csv files storing the tokens."""

        missing_files = self._get_missing_files()
        if missing_files == []:
            self._load_user_file()
            self._load_tstat_file()
        elif len(missing_files) == 1:
            self.raise_file_missing_error(missing_files)
        else:
            self._init_new_files()

    def _load_user_file(self):
        """Load the user file."""

        index_name = 'user_id'
        dtype = {'user_id': str, 'access_token': str, 'refresh_token': str}
        self._user = pd.read_csv(self.config.user_file, dtype=dtype)
        self._user.set_index(index_name, inplace=True)

    def _load_tstat_file(self):
        """Load the thermostat file."""

        index_name = 'tstat_id'
        dtype = {'tstat_id': str, 'user_id': str}
        self._tstat = pd.read_csv(self.config.tstat_file, dtype=dtype)
        self._tstat.set_index(index_name, inplace=True)

    def _get_missing_files(self):
        """Return a list of the missing token files."""

        missing_files = []
        for fname in [self.config.user_file, self.config.tstat_file]:
            if not os.path.exists(fname):
                missing_files.append(fname)
        return missing_files

    def raise_file_missing_error(self, missing_files):
        """Raise an data corruption error listing the files which are missing."""

        err_msg = "Data Corrupted {} Missing.".format(missing_files[0])
        raise EnvironmentError(err_msg)

    def _init_new_files(self):
        """Create new token files."""

        user_cols = ["user_id", "access_token", "refresh_token"]

        self._user = pd.DataFrame(columns=user_cols)
        self._user.set_index("user_id", inplace=True)

        tstat_cols = ["tstat_id", "user_id"]

        self._tstat = pd.DataFrame(columns=tstat_cols)
        self._tstat.set_index("tstat_id", inplace=True)

        self._save_files()

    def _save_files(self):
        """Store the tokens to local files."""

        self._save_user_file()
        self._save_tstat_file()

    def _save_user_file(self):
        """Store the users to a local file."""

        self._user.to_csv(self.user_file)

    def _save_tstat_file(self):
        """Store the thermostats to a local file."""

        self._tstat.to_csv(self.tstat_file)

    def refresh(self):
        """Refresh tokens for each user."""

        for idx, row in self._user.iterrows():
            ref = row["refresh_token"]
            try:
                self._user.loc[idx] = self.refresh_token(ref)
            except Exception:
                pass
            finally:
                self._save_user_file()

    def get_next_user_id(self):
        """Return the next internal user id."""

        user_id = len(self._user) + 1
        logger.info("Generating New User ID: %s", user_id)
        return user_id

    def delete(self, tstat_id):
        """Removes the supplied thermostat from the thermostat tokens."""

        if not self.has_tstat(tstat_id):
            raise KeyError(self.unknown_tstat.format(tstat_id))

        user_id = self._tstat.loc[tstat_id, "user_id"]
        self._drop_tstat(tstat_id)

        if user_id not in self._tstat.user_id.unique():
            self._drop_user(user_id)
        self._save_files()

    def has_tstat(self, tstat_id):
        """Returns true if the tokens exist for the supplied thermostat."""

        return tstat_id in self._tstat.index

    def has_user(self, user_id):
        """Returns true if the toekens exist for the supplied user."""

        return user_id in self._user.index

    def _drop_tstat(self, tstat_id):
        """Drops the supplied thermostat from the thermostats file."""

        logger.info("Droping Tstat %s", tstat_id)
        self._tstat.drop(tstat_id, inplace=True)
        self._save_tstat_file()

    def _drop_user(self, user_id):
        """Drops the supplied user from the users file."""

        logger.info("Droping User %s", user_id)
        self._user.drop(user_id, inplace=True)
        self._save_user_file()

    def insert(self, user_id, tstat_id, acc, ref):
        """Inserts a new user device combination."""

        self.insert_user(user_id, acc, ref)
        self.insert_tstat(user_id, tstat_id)

    def insert_user(self, user_id, acc, ref):
        """Inserts a new user."""

        if user_id in self._user.index:
            raise RuntimeError("Attempt to overwrite user {}".format(user_id))
        self._user.loc[user_id] = [acc, ref]
        self._save_user_file()

    def insert_tstat(self, user_id, tstat_id):
        """Inserts a new thermostat."""

        if tstat_id in self._tstat.index:
            msg = "ID: {} Already entered for User: {}".format(tstat_id, user_id)
            raise ResourceWarning(msg)

        self._tstat.loc[tstat_id] = user_id
        self._save_tstat_file()

    def get_access_token(self, tstat_id):
        """Return the access token for the supplied thermostat identifier."""

        try:
            user_id = self._tstat.loc[tstat_id, "user_id"]
            return self.lookup_access_token(user_id)
        except KeyError:
            raise KeyError(self.unknown_tstat.format(tstat_id))

    def lookup_access_token(self, user_id):
        """Return the access token for a particular user."""

        try:
            row_counts = self._user.index.value_counts()
            row_num = row_counts[user_id]
            if row_num > 1:
                raise ValueError("Corrupted State Multiple rows found for User {}".format(user_id))
            return self._user.loc[user_id, "access_token"]
        except KeyError:
            msg = "No tokens found for user {}".format(user_id)
            raise KeyError(msg)

    def display_tokens(self):
        """Displays the tokens files."""

        print("Users")
        print(self._user)
        print()
        print("Thermostats")
        print(self._tstat)
        print()

    def refresh_token(self, ref_token, api_key):
        """Refreshe the tokens for a single thermostat."""

        logger.info("Original refresh_tokens")

        headers = {"Content-Type": "application/json;charset=UTF-8"}
        url = 'https://api.ecobee.com/token'
        params = {"grant_type": "refresh_token",
                  "code": ref_token,
                  "client_id": api_key}
        resp = requests.post(url, params=params, headers=headers)
        jsn = resp.json()
        try:
            tokens = (jsn["access_token"], jsn["refresh_token"])
            return tokens
        except KeyError:
            raise RuntimeError("Error parsing Json:\n {}".format(jsn))
