import io

import pandas as pd
import qrcode

from SuperSTATs.utils.constants import ALLIANCE_SIZE


def get_match_scouts(team: list[str], match_list: list[str], rotation: int) -> dict:
    """Map each match name to the alliance-sized group of scouts assigned to it."""
    scouts = {}
    count = 0
    i = 0
    while len(scouts) < len(match_list):
        group = [team[(count - j) % len(team)] for j in range(ALLIANCE_SIZE)]
        if i % rotation == 0:
            count += 1
        if count == len(team):
            count = 0
        for match_type in ["Quals", "Playoffs", "Finals"]:
            for j in range(rotation):
                name = f"{match_type} {i + 1 + j}"
                if name in match_list:
                    scouts[name] = group
        i += rotation
    return scouts


def get_all_match_scouts(
    assigned: list[str], match_list: list[str], rotation: int
) -> dict[str, list[str]]:
    """Red scouts (even indexes) then blue scouts (odd indexes) per match."""
    red = get_match_scouts(assigned[::2], match_list, rotation)
    blue = get_match_scouts(assigned[1::2], match_list, rotation)
    return {m: red[m] + blue[m] for m in match_list}


def match_teams(matches: pd.DataFrame) -> pd.DataFrame:
    """Index: Match Name. Columns: Red 1-3, Blue 1-3 (from TBA matches)."""
    teams = {}
    for name, row in matches.set_index("Match Name").iterrows():
        teams[name] = row["🔴 Teams"] + row["🔵 Teams"]
    cols = [f"{c} {i + 1}" for c in ("Red", "Blue") for i in range(ALLIANCE_SIZE)]
    return pd.DataFrame.from_dict(teams, orient="index", columns=cols)


def gen_qr(contents: str) -> bytes:
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L)
    qr.add_data(contents)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#ffffff", back_color="#141414")
    stream = io.BytesIO()
    img.save(stream, format="JPEG")
    return stream.getvalue()
