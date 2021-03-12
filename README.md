
# Splunk Project
This project adds user either from `data_characters.csv` or from the admin's input, deletes user, modifies roles of a user, and resets the password of a user in the Splunk Enterprise. Alongside, it automates to create/delete user credentials in csv, txt, and in Google Sheets.

## Python modules requirements to run this project:
In order to run this project, here are the python modules needed to install:
```bash
pip install gspread
pip install oauth2client
pip install splunk-sdk
```
In addition, you need credentials for the Splunk Enterprise to get access to the Splunk Enterprise server. After getting the credentials for the Splunk Enterprise, import the `keyring` module to interface with your Mac/Windows/Linux's key chain and to store the password there. In addition, import the `os` module to store the username as environment variables.  

Moreover, you need the oauth2 credentials in order to run the Google Sheets automation in Python. These oauth2 credentials should be put into a file called `creds.json`.

To run the project, run `python3 splunky.py` to the interpreter.
If you want the script to run without invoking the interpreter you would run it as `#!/usr/bin/python3`.
