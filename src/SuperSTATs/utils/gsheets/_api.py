import pandas as pd

from SuperSTATs.utils.constants import DEFAULT_GSHEET_DOC_ID


def get_data(sheet_id: str, doc_id: str = DEFAULT_GSHEET_DOC_ID):
    """
    Downloads a Google Sheets document as a pandas DataFrame.

    Args:
        doc_id (str): The ID of the Google Sheets document.
        sheet_id (str): The ID of the specific sheet within the document.

    Returns:
        pandas.DataFrame: The downloaded Google Sheets document as a DataFrame.
    """
    print("\t⬇️ Fetching Google Sheets data")
    sheet_url = f"https://docs.google.com/spreadsheets/d/{doc_id}/export?format=csv&gid={sheet_id}"
    df = pd.read_csv(sheet_url)
    df.columns = (
        df.columns.str.lstrip()
        .str.replace("[", repl="", regex=False)
        .str.replace("]", repl="", regex=False)
    )
    return df
