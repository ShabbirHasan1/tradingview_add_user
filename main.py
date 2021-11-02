import sys

from trading_view_session import TradingViewSession
from google_sheet import get_google_sheet_value
from gui_utils import get_row_to_begin
import config


def get_users_pack_to_add():
    """
    return a dict {user : (pack_script, pack_expiration)}
    """
    start_raw = get_row_to_begin()
    users_to_add = dict()
    sheet_value = get_google_sheet_value(config.SPREADSHEET_ID)
    for row in sheet_value[(int(start_raw)-1):]:
        username = row[3]
        pack_scripts = row[0]
        pack_expiration = row[4]
        users_to_add[username] = (pack_scripts, pack_expiration)

    return users_to_add


def main():
    users_to_add = get_users_pack_to_add()

    # Init the session (cookies, login etc...)
    trading_view_session = TradingViewSession()
    if not trading_view_session.init_session():
        sys.exit(1)
    # Adds the user to their pack
    for user, (pack_scripts, pack_expiration) in users_to_add.items():
        trading_view_session.handle_new_user(user, pack_scripts, pack_expiration)


if __name__ == '__main__':
    main()
    sys.exit(0)
