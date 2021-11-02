#################################
# To configure with the client:
# 	- SPREADSHEET_ID
#	- google_account_api_path
#	- folder_base_path
#	- The script names field
#	- The pack values
#	- The expiration values
#	- Tradingview credentials
#################################

# TradingView credentials
username = ''
password = ''

# Scripts names field
SCRIPT_NAME_1 = 'NAME'
SCRIPT_NAME_2 = 'NAME'

# Configure the scripts for each pack
pack_script_map = {
    'Pack1': [SCRIPT_NAME_1],
    'Pack2': [],
    'Pack3': []
}

NO_EXPIRATION_DATE = -1
# Configure the field in the google sheet that define the expirations date packs
pack_expiration_map = {
    '6month': 6,
    '1year': 12,
    '2years': 24,
    'no expiration': NO_EXPIRATION_DATE
}

# The folder that contains all the code
folder_base_path = ''
# The path to the tradingview session details
session_details_path = "{base_folder}session_details.json".format(base_folder=folder_base_path)
# The path for the log file
log_filename = "{base_folder}log.txt".format(base_folder=folder_base_path)

# The path to the json key of the google authentication
google_account_api_path = "{base_folder}key.json".format(base_folder=folder_base_path)

# The id of the google sheet
SPREADSHEET_ID = ''
