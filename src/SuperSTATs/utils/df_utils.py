import pandas as pd


def normalize_column(df, column_name):
    return pd.concat([df, pd.json_normalize(df[column_name])], axis=1).drop(
        columns=column_name
    )
