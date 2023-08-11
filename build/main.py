#------------------------------------------------------------------------------------
#Copyright (c) 2023, MalkasianGroup, LLC - All rights reserved.
#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------
# DO NOT DELETE THIS FILE - SYSTEM WILL NOT BOOT OR RUN.
#------------------------------------------------------------------------------------
import gc
import urequests
import re
import _thread
from PicoOS import connect_wifi, pico_os_main, deliver_current_version

gc.collect()
connect_wifi()

# LOGIC FLOW:
# Connect Wifi
# Get system up and running
# Use additional thread to check for update (if update False, check in 7 days.)
    # If no update, return "System up to date" and no button shows on web page.
    # If update found, then "update system to" "curent OS __version" appears.
# def deliver_current_version(__version__):
#     local_version = '.'.join(str(i) for i in __version__)
#     print(f"CURRENT VERSION: {local_version}")
#     return __version__



def get_version_number(remote_version_url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = urequests.get(remote_version_url, headers=headers)
        if response.status_code == 200:
            match = re.search(r'__version__ = \((\d+,\d+,\d+)\)', response.text)
            if match:
                version_string = match.group(1)  # Extract the version string
                version_components = tuple(map(int, version_string.split(',')))
                return version_components
    except Exception as e:
        print("Error:", e)
    return None


try:
    local_version = deliver_current_version()
    remote_version_url = 'http://raw.githubusercontent.com/smalkasian/Pico-W-LED-Controller/main/build/PicoOS.py'
    remote_version = get_version_number(remote_version_url)
    response = urequests.get(remote_version_url)
    print("Status Code:", response.status_code)

    if remote_version:
        print(f"Current OS version: {local_version}")
        print(f"There is an update available ({remote_version}).")
    else:
        print("Update check failed. Try again later.")
except Exception as e:
    print("Error:", e)


#------------------------------------------------------------------------------------
#----------------------------------MAIN PROGRAM---------------------------------------




# pico_os_main()
