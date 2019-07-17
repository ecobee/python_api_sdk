"""This module stores constants related to enviornment variables."""

EV_APP_KEY = "ECOBEE_APPLICATION_KEY"
EV_USER_TOKEN_FILE = "EBAPI_USER_TOKENS_FILE"
EV_USER_TSTAT_FILE = "EBAPI_USER_TSTAT_FILE"

REQUIRED_EVS = [EV_APP_KEY, EV_USER_TOKEN_FILE, EV_USER_TSTAT_FILE]

def validate_enviornment():
    """Return a list of the the enviornment variables not found."""
       
    missing_evs = [ev for ev in env_vars.REQUIRED_EVS if ev not in os.environ.keys()]

    if missing_evs:
        err_fmt = "Could not find EBAPI enviornment variabel(s): {}"
        err_msg = err_fmt.format(", ".join(missing_evs))
        raise EnvironmentError(err_msg)
validate_enviornment()

USER_FILE = os.environ[env_vars.EV_USER_TOKEN_FILE]
TSTAT_FILE = os.environ[env_vars.EV_USER_TSTAT_FILE]
APP_KEY = os.environ[env_vars.EV_APP_KEY]


