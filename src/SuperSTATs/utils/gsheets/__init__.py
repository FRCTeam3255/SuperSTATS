from SuperSTATs.utils import constants
from SuperSTATs.utils.gsheets import _api


def get_input_data():
    df = _api.get_data(constants.RAW_INPUT_SHEET_ID)
    df = df.loc[df["Event Key"] == constants.DEFAULT_EVENT_KEY]
    return df
