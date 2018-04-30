"""A connection to the ecobee API."""

import os
import requests
import json
import copy
from .tokens import FileTokens as Tokens
import sys
import logging

url_base = 'https://api.ecobee.com/'
version = '1/'
app_key = os.environ["ECOBEE_APPLICATION_KEY"]

logger = logging.getLogger(__name__)

if app_key == "":
    raise ValueError("Appliection KEY has not been initilized. Please set a ECOBEE_APPLICATION_KEY enviornment variable")

class ApiConnection:
    """A connection to send requests to the Ecobee API.

    This module presumes that you are only ever
    sending and reciving from one thermostat"""

    url = url_base + version + 'thermostat'
    basic_selection = {"selectionType": "thermostats"}

    def __init__(self, verbose=False):
        self.tokens = Tokens()

    def refresh_tokens(self):
        self.tokens.refresh()

    def gen_headers(self, identifier):
        access_token = self.tokens.get_access_token(identifier)
        headers = {"Content-Type": "application/json;charset=UTF-8",
                   "Authorization": "Bearer " + str(access_token)}
        return headers

    def format_selection(self, identifier):
        selection = copy.deepcopy(self.basic_selection)
        selection["selectionMatch"] = identifier
        return selection

    def add_selection(self, body, identifier):
        selection = self.format_selection(identifier)
        try:
            for key, val in body["selection"].items():
                selection[key] = val
        except KeyError:
            pass
        body["selection"] = selection

        return body

    def send_get(self, body, identifier):
        headers = self.gen_headers(identifier)
        body = self.add_selection(body, identifier)
        params = {'format': 'json', 'body': json.dumps(body)}
        kwargs = {"headers": headers,
                  "params": params}
        resp = self.attempt(requests.get, identifier, **kwargs)
        return resp["thermostatList"][0]

    def send_post(self, body, identifier):
        headers = self.gen_headers(identifier)
        body = self.add_selection(body, identifier)
        params = {'format': 'json'}
        kwargs = {"headers": headers,
                  "params": params,
                  "data": json.dumps(body)}
        return self.attempt(requests.post, identifier,  **kwargs)

    def attempt(self, func, identifier,  **kwargs):
        self.log_attempt(func, identifier, **kwargs)
        try:
            resp = self.send_request(func, **kwargs)
        except ExpiredTokenError:
            self.refresh_tokens()
            kwargs["headers"] = self.gen_headers(identifier)
            resp = self.send_request(func, **kwargs)
        return resp

    def log_attempt(self, func, identifier, **kwargs):
        log = "Running {} request\n".format(func.__name__)
        log += "On Thermostat {}\n".format(identifier)
        log += "Args:\n"
        log += format_dict(kwargs)
        logger.debug(log)
    
    def send_request(self, func, **kwargs):
        # API response codes
        EXPIRED_TOKEN = 14
        SUCCESS = 0
        resp = func(self.url, **kwargs).json()
        code = resp["status"]["code"]
        if code == SUCCESS:
            return resp
        elif code == EXPIRED_TOKEN:
            raise ExpiredTokenError("Access token is expired")
        else:
            msg = resp["status"]["message"]
            raise ApiError("Api Request Failed With Code: {}\n{}".format(code, msg))

    def send_functions(self, functions, identifier):
        batches = get_chunks(functions, 10)
        results = []
        for batch in batches:
            body = {"functions": batch}
            result = self.send_post(body, identifier)
            results.append(result)
        return results

    def add_user(self):
        """Get tokens and add them to database.

        It gives the user they're pin and requests they authorize it.
        It then enters that Tstats Identifier, access_toeken and
        refresh_token into the RDS ecobee.IRS_API_KEYS Table.
        """

        pin, code = self.get_auth_pin()       
        print("Enter the PIN '{}' into the Add Application window and click Add Application".format(pin))
        input("waiting press enter to continue...")

        access_token, refresh_token = self.get_tokens(code)
        user_id = self.tokens.get_next_user_id()
        self.tokens.insert_user(user_id, access_token, refresh_token)
        tstat_ids = self.get_tstat_ids(access_token)
        for tstat_id in tstat_ids:
            logger.info("Adding Thermostat ID: {}".format(tstat_id))
            self.tokens.insert_tstat(user_id, tstat_id)


    def get_tstat_ids(self, acc):
        headers = {"Content-Type": "application/json;charset=UTF-8",
                   "Authorization": "Bearer " + acc}
        url = url_base + version + 'thermostat'
        selection = {"selectionType": "registered", "selectionMatch": ""} 
        params = {'format': 'json',
                  'body': json.dumps({"selection": selection})}
        resp = requests.get(url, headers=headers, params=params).json()
        tstat_ids = [tstat['identifier'] for tstat in resp['thermostatList']]
        return tstat_ids

    def get_auth_pin(self):
        """Get an authorization pin for the ecobee binary schedule app."""
        url = url_base + "authorize"
        params = {"response_type": "ecobeePin",
                  "client_id": app_key,
                  "scope": "smartWrite"}
        resp = requests.get(url, params=params)
        try:
            resp_json = resp.json()
        except:
            raise ValueError("Response Could not be translated to json {}".format(resp))
        return resp_json["ecobeePin"], resp_json["code"]

    def get_tokens(self, code):
        """Get the tokens for a user once they have entered the auth pin."""
        url = url_base + "token"
        params = {"grant_type": "ecobeePin", "code": code, "client_id": app_key}
        temp = requests.post(url, params=params).json()
        return (temp["access_token"], temp["refresh_token"])

def get_chunks(vals, size):
    """Break vals in to batches of length size."""
    for i in range(0, len(vals), size):
        yield vals[i:i + size]



def format_dict(dictionary, depth=0):
    """Returns dictionaries to a formated string"""
    tab = " " * 4
    string = "{\n"
    for key, val in dictionary.items():
        string += depth * tab 
        string += "{}: ".format(key)
        if type(val) is dict:
            string += format_dict(val, depth + 1)
                
        else:
            if type(val) is str:
                fmt = "'{}'\n"
            else:
                fmt = "{}\n"
            string += fmt.format(val)
    string += (depth) * tab + '}\n'
    return string
class ApiError(Exception):

    def __init__(self, *args, **kwargs):

        Exception.__init__(self, *args, **kwargs)


class ExpiredTokenError(ApiError):

    def __init__(self, *args, **kwargs):

        ApiError.__init__(self, *args, **kwargs)
