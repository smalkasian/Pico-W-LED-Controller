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
import time
from PicoOS import connect_wifi, pico_os_main, deliver_current_version

def check_remote_version():
    try:
        remote_version_url = 'http://raw.githubusercontent.com/smalkasian/Pico-W-LED-Controller/main/build/PicoOS.py'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = urequests.get(remote_version_url, headers=headers)
        print("Status Code:", response.status_code)
        if response.status_code == 200:
            match = re.search(r'__version__ = \((\d+,\d+,\d+)\)', response.text)
            if match:
                version_string = match.group(1)  # Extract the version string
                version_components = tuple(map(int, version_string.split(',')))
                return version_components
    except Exception as e:
        print("Error:", e)
    return None

def update_software(action): #NEEDS TO BE CONNECTED TO THE LOGIC WITHIN PICOOS.PY
    if action == 'update_software':
        print("Updating software...")
        update_url = 'http://raw.githubusercontent.com/smalkasian/Pico-W-LED-Controller/main/build/PicoOS.py'
        try:
            response = urequests.get(update_url)
            if response.status_code == 200:
                update_content = response.text()
                # Write the content to a local file (replace existing file)
                with open("PicoOS.py", "w") as f:
                    f.write(update_content)
                print("Update completed successfully.")
            else:
                print("Failed to fetch the update.")
        except Exception as e:
            print("Update failed:", e)

def check_for_update_verbose():
    try:
        print("Checking for system update")
        local_version = deliver_current_version()
        remote_version = check_remote_version()
        print(f"{local_version} | {remote_version}")
        if remote_version == local_version:
            print("System is up to date!")
        elif remote_version != local_version:
            print("There's an update available. Would you like to update?")
            print("-------------------------------------------------")
            print(f"Current OS version: {local_version}")
            print("")
            print(f"There is an update available ({remote_version}).")
            print("-------------------------------------------------")
            user_answer = input("yes/no: ")
            if user_answer == 'yes':
                update_software()
        else:
            print("Update check failed. Try again later.")
    except Exception as e:
        print("Error:", e)

def check_for_update():
    try:
        local_version = deliver_current_version()
        remote_version = check_remote_version()
        if remote_version == local_version:
            pass
        elif remote_version != local_version:
            update_message = f"Version {remote_version} is available."
            return update_message
        else:
            print("FAILED TO GET UPDATE")
    except Exception as e:
        print("Error:", e)
#-------------------------------------------------------------------------------------

#----------------------------------MAIN PROGRAM---------------------------------------


gc.collect()
connect_wifi()
check_for_update_verbose()
time.sleep(5)
pico_os_main()