import requests
import re
import html
import json
import logging
import datetime
from dateutil.relativedelta import relativedelta

import config

BASE_TRADING_VIEW_URL = 'https://www.tradingview.com'
SIGNIN_URL = '{url}/accounts/signin/'.format(url=BASE_TRADING_VIEW_URL)
INVITE_USER_URL = '{url}/pine_perm/add/'.format(url=BASE_TRADING_VIEW_URL)
SCRIPT_BASE_URL = '{url}/script{{script_url}}'.format(url=BASE_TRADING_VIEW_URL)
SCRIPTS_INFO_URL = '{url}/api/v1/user/profile/charts/?script_type=all&access_script=all&privacy_script=all&by={{user_id}}'.format(
    url=BASE_TRADING_VIEW_URL)
DATE_EXPIRATION_FORMAT = '{year}-{month}-{day}T23:59:59.999Z'

SCRIPT_URL_KEY = 'script_url'
PINE_ID_KEY = 'pine_id'


class TradingViewSession():
    def __init__(self):
        self.username = config.username
        self.password = config.password
        self.logged_in = False
        self.http_session = requests.Session()
        self.session_details = {}
        self.scripts_info = {}
        self.__config_logger()

    def init_session(self):
        try:
            self.logger.debug('-------------------- NEW SCRIPT EXECUTION --------------------')
            self.__init_session_details()
            if not self.scripts_info:
                self.__init_scripts_info()
            self.logger.debug('The session has been successfully initialized')
            return True
        except LoginError:
            self.logger.debug('Got an exception while logging in', exc_info=True)
            return False
        except Exception:
            self.logger.debug("Error while initializing session", exc_info=True)
            return False

    def handle_new_user(self, username_to_add, script_pack, expiration_pack):
        """
        Adds the user name to every script he submitted to according to the pack
        """
        try:
            expiration_date = self.__get_expiration_date_by_pack(expiration_pack)
            for script_name in config.pack_script_map[script_pack]:
                self.__invite_user_to_a_script(username_to_add, script_name, expiration_date)
        except UserAddError:
            self.logger.debug('Got an exception while adding a user', exc_info=True)
            return False
        except Exception:
            self.logger.debug('Got an exception while handling new user', exc_info=True)
            return False

    def __init_scripts_info(self):
        response = self.http_session.get(SCRIPTS_INFO_URL.format(user_id=self.session_details['user_id']))
        self.scripts_info = self.__extract_script_infos(response.text)

    def __extract_script_infos(self, response):
        scripts_info = dict()
        unescaped = html.unescape(response)
        scripts = unescaped.split('current_user')[1:]
        for script in scripts:
            scripts_info.update(self.__extract_single_script_infos(script))
        return scripts_info

    def __set_cookies(self):
        self.http_session.cookies.set('sessionid', self.session_details['sessionid'], domain=".tradingview.com")
        self.http_session.cookies.set('device_t', self.session_details['device_t'], domain=".tradingview.com")

    def __init_session_details(self):
        self.session_details = self.__get_old_session_details()
        self.logger.debug('Got older session details')
        if self.session_details and self.session_details['user_id'] and self.session_details['sessionid'] and self.session_details['device_t']:
            self.__set_cookies()
            self.__init_scripts_info()
            if not self.scripts_info:
                self.logger.debug('Cannot connect with the old session details, logging in from the beginning')
                self.__login()
            else:
                self.logger.debug('Connected with older session details')
        else:
            self.logger.debug('Connecting with new session details')
            self.__login()

    def __login(self):
        data = {"username": self.username, "password": self.password, "remember": "on"}
        headers = {'Referer': BASE_TRADING_VIEW_URL}
        response = self.http_session.post(url=SIGNIN_URL, data=data, headers=headers)

        if response.json()['error']:
            self.logger.debug('An error has occurred during sending the loging in, error: {error}'.format(
                error=response.json()['error']))
            raise LoginError('Cannot login, got an error')
        self.logger.debug('Successfully authenticated to tradingview')
        self.__parse_session_details(response)
        self.logger.debug('Successfully parsed session details')

    def __parse_session_details(self, response):
        self.session_details['user_id'] = str(response.json()['user']['id'])
        self.session_details['sessionid'] = self.http_session.cookies.get_dict()['sessionid']
        self.session_details['device_t'] = self.http_session.cookies.get_dict()['device_t']
        with open(config.session_details_path, 'w') as session_details_file:
            json.dump(self.session_details, session_details_file)

    def __invite_user_to_a_script(self, username_to_add, script_name, expiration_date):
        """
        Invite a single user to a script by its name
        """
        script_url = self.scripts_info[script_name][SCRIPT_URL_KEY]
        headers = {'Referer': SCRIPT_BASE_URL.format(script_url=script_url)}
        data = {"pine_id": self.scripts_info[script_name][PINE_ID_KEY], "username_recip": username_to_add}
        if expiration_date is not None:
            data.update({"expiration": expiration_date})
        response = self.http_session.post(url=INVITE_USER_URL, data=data, headers=headers)
        if response.json()['status'] == 'exists':
            self.logger.debug('The user {user} already exist for the script {script}'.format(user=username_to_add, script=script_name))
        elif response.json()['status'] == 'ok':
            self.logger.debug('Successfully added the user: {user} to the script {script}'.format(user=username_to_add, script=script_name))
        else:
            self.logger.debug('Unexpected status for adding {user} to the script {script} - status: [{status}]]'.format(user=username_to_add, script=script_name, status=response.json()['status']))
            raise UserAddError('Status unexpected')

    def __config_logger(self):
        logging.basicConfig(filename=config.log_filename,
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

        self.logger = logging.getLogger('TradingView')

    @staticmethod
    def __get_old_session_details():
        with open(config.session_details_path, 'r') as session_details:
            data = json.load(session_details)
        return data

    @staticmethod
    def __extract_single_script_infos(script):
        relevant_part = str(re.findall('"published_chart_url":".*","short_symbol', script)[0])
        script_url = (relevant_part.split('":"')[1].split('","')[0]).strip(' ')
        script_name = (relevant_part.split('":"')[2].split('","')[0]).strip(' ')
        pine_id = str(re.findall('PUB;.*', script)[0].split('\\')[0]).strip(' ')

        return {script_name: {PINE_ID_KEY: pine_id, SCRIPT_URL_KEY: script_url}}

    @staticmethod
    def __get_expiration_date_by_pack(expiration_pack):
        months_to_add = config.pack_expiration_map[expiration_pack]
        if months_to_add is config.NO_EXPIRATION_DATE:
            return None
        future_date = datetime.datetime.now() + relativedelta(months=months_to_add)
        return DATE_EXPIRATION_FORMAT.format(year=future_date.year, month=future_date.month, day=future_date.day)


class LoginError(Exception):
    pass


class UserAddError(Exception):
    pass
