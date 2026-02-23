import pandas as pd

from SuperSTATs.utils.constants import DEFAULT_GSHEET_DOC_ID


def get_data(doc_id=DEFAULT_GSHEET_DOC_ID, sheet_id=None):
    """
    Downloads a Google Sheets document as a pandas DataFrame.

    Args:
        doc_id (str): The ID of the Google Sheets document.
        sheet_id (str): The ID of the specific sheet within the document.

    Returns:
        pandas.DataFrame: The downloaded Google Sheets document as a DataFrame.
    """
    sheet_url = f"https://docs.google.com/spreadsheets/d/{doc_id}/export?format=csv&gid={sheet_id}"
    df = pd.read_csv(sheet_url)
    df.columns = (
        df.columns.str.lstrip()
        .str.replace("[", repl="", regex=False)
        .str.replace("]", repl="", regex=False)
    )
    return df
