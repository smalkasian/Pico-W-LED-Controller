#------------------------------------------------------------------------------------
#Copyright (c) 2023, MalkasianGroup, LLC - All rights reserved.
#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------
# DO NOT DELETE THIS FILE - SYSTEM WILL NOT BOOT OR RUN.
#------------------------------------------------------------------------------------

import gc
import urequests
import ure as re
from PicoOS import connect_wifi, pico_os_main

gc.collect()
connect_wifi()

# def deliver_current_version(__version__):
#     local_version = '.'.join(str(i) for i in __version__)
#     print(f"CURRENT VERSION: {local_version}")
#     return __version__


# local_version = deliver_current_version(__version__)
remote_version_url = 'https://raw.githubusercontent.com/smalkasian/Pico-W-LED-Controller/main/build/PicoOS.py'

def get_version_number(remote_version_url):
    response = urequests.get(remote_version_url)
    if response.status == 200:
        match = re.search(r'__version__ = \((\d+,\d+,\d+)\)', response.text)
        if match:
            return match.group(0)
    return None

# print("Local Version: " + __version__)
print("Remote Version: " + str(get_version_number(remote_version_url)))


# I need the function to check what's in the PicoOS and update that here.
# It then checks the file in the main foder and compares. It doesn't update
# locally in main.py until the file is successfully downloaded. Everything
# within those programs need to be updated. The only issue is that
# everything needs to be a function. I need to make the entire file run 
# under a single function. "PicoOS.run()"


# scripts for OTA updates here
# scripts for running main OS in here
# Instructions on how to run the system in here

#------------------------------------------------------------------------------------
#----------------------------------MAIN PROGRAM---------------------------------------




# pico_os_main()
