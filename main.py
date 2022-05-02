# !pip install tk
import io
import os
import tkinter as tk
from tkinter import ttk
import json
from os import path
from datetime import datetime
from time import sleep

# Google Api Imports
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload

from tools.gpio_control import Control

DEBUG_MODE = False
google_drive_connected = False
FREQ_KEY = 'food_freq_var'
AMT_KEY = 'food_amt_var'
TEMP_KEY = 'tank_temp_var'

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 600
WINDOW_GEOMETRY = str(WINDOW_WIDTH) + 'x' + str(WINDOW_HEIGHT)
LABEL_PADDING = (20, 5)
JSON_FILE_NAME = 'smart_tank_config.json'
json_config = None
JSON_FILE_DEFAULTS = {
    FREQ_KEY: '12',
    AMT_KEY: '1',
    TEMP_KEY: 70.0
}
SCOPES = ['https://www.googleapis.com/auth/drive']
CONVERSION_FACTORS = {
    FREQ_KEY: 1,
    AMT_KEY: 1,
    TEMP_KEY: 1
}

drive_service = None
controller = Control()


def login_redirect_google():
    global drive_service, DEBUG_MODE
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        drive_service = build('drive', 'v3', credentials=creds)
        print('Logged in to Google Drive.')
        google_drive_connected = True
        if DEBUG_MODE:
            # Call the Drive v3 API
            results = drive_service.files().list(
                pageSize=10, fields="nextPageToken, files(id, name)").execute()
            items = results.get('files', [])

            if not items:
                print('No files found.')
                return
            print('Files:')
            for item in items:
                print(u'{0} ({1})'.format(item['name'], item['id']))
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')


login_redirect_google()

JSON_MIME = 'application/json'
# file_metadata = {'name': 'smart_tank_config.json'}
# file_media = MediaFileUpload('smart_tank_config.json', mimetype=JSON_MIME)
# file = drive_service.files().create(body=file_metadata, media_body=file_media, fields='id').execute()

# Init of root/frame
root = tk.Tk()
root.title('Smart Fish Tank Control')
root.geometry(WINDOW_GEOMETRY)
root.resizable(False, False)
frame = ttk.Frame(root, height=575, width=375, borderwidth=10)
frame.grid(row=1, column=1)

# Tkinter Vars (do not move from here)
# Must be below root init but above json loading
# Food Frequency Var
food_freq_var = tk.StringVar()
# Food Amount Var
food_amt_var = tk.StringVar()
# Tank Temperature Var
tank_temp_var = tk.DoubleVar()
# Tank Temperature Label
temp_str = tk.StringVar()


# When save_changes_btn is clicked, save current settings and make changes to PID process.
def save_changes_button():
    global tank_temp_var, food_freq_var, food_amt_var
    print('Saving changes')

    # Debug vars
    print('food_freq_var:', food_freq_var.get())
    print('food_amt_var:', food_amt_var.get())
    print('tank_temp_var:', tank_temp_var.get())

    save_json_config()
    sync_json_to_google_drive()


def sync_json_to_google_drive():
    global drive_service, json_config, JSON_FILE_NAME
    if drive_service is None or not google_drive_connected:
        print('Google Cloud syncing is offline. \nPlease relaunch the app to retry, or continue using in Offline Mode.')

    localcopy_lastmod = datetime.fromtimestamp(path.getmtime(JSON_FILE_NAME))
    print(type(localcopy_lastmod))
    print('Local version was last modified at:', localcopy_lastmod)
    print('Syncing to Google Drive...')
    g_file = drive_service.files().list(pageSize=10, q=f"name ='{JSON_FILE_NAME}'",
                                        fields="nextPageToken, files(id, name, modifiedTime, createdTime)").execute()
    items = g_file.get('files', [])
    if items is None:
        print('Could not retrieve files from Google Drive.')
        print('Uploading local version to Drive.')
        file_metadata = {'name': 'smart_tank_config.json'}
        file_media = MediaFileUpload('smart_tank_config.json', mimetype=JSON_MIME)
        drivecopy = drive_service.files().create(body=file_metadata, media_body=file_media, fields='id').execute()
        return

    for drivecopy in items:
        drivecopy_lastmod = drivecopy.get('lastModified')
        drivecopy_id = drivecopy.get('id')

        print(type(drivecopy_lastmod))
        print('Google Drive version was last modified:', drivecopy_lastmod)
        if localcopy_lastmod > drivecopy_lastmod:
            # This means that the local copy is newer
            drive_service.files().delete(fileId=drivecopy_id)  # Delete the current drive copy

            upload_localcopy_to_google_drive()  #
        elif localcopy_lastmod < drivecopy_lastmod:
            replace_local_with_remote_json(drivecopy_id)
        else:
            pass
            # This means that the local and google drive copies are the same last modified.
            print('Versions are synced between drive and local copy.')


def upload_localcopy_to_google_drive():
    global JSON_FILE_NAME
    file_metadata = {'name': JSON_FILE_NAME}
    file_media = MediaFileUpload(JSON_FILE_NAME, mimetype=JSON_MIME)
    drivecopy = drive_service.files().create(body=file_metadata, media_body=file_media, fields='id').execute()
    print('Uploaded local copy to Google Drive.')


def replace_local_with_remote_json(drivecopy_id):
    global drive_service
    # this means that the local copy is older
    os.remove(JSON_FILE_NAME)  # delete local copy
    # Start download process
    request = drive_service.files().get_media(fileId=drivecopy_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f'Downloading... {int(status.progress() * 100)}%')
    print('Download complete.')


def load_json_config():
    global food_freq_var, food_amt_var, tank_temp_var, \
        json_config, JSON_FILE_DEFAULTS, JSON_FILE_NAME, \
        TEMP_KEY, FREQ_KEY, AMT_KEY
    # Check if JSON config file exists
    if path.exists(JSON_FILE_NAME):
        # Read JSON config file
        with open(JSON_FILE_NAME, 'r') as file:
            json_config = json.loads(file.read())
            print('JSON Config File Found:', json_config)
    else:
        # Initialize JSON config file
        json_config = JSON_FILE_DEFAULTS
        print('Initializing JSON File Config Defaults.')
        # save_json_config()

    # Load JSON Configs into Vars
    food_freq_var.set(json_config.get(FREQ_KEY))
    food_amt_var.set(json_config.get(AMT_KEY))
    temp_dbl = JSON_FILE_DEFAULTS[TEMP_KEY]
    print('config test', json_config.get(TEMP_KEY))
    try:
        temp_dbl = float(json_config.get(TEMP_KEY))
    except ValueError as e:
        print('Configuration file has been incorrectly altered. Setting Tank Temperature to default value.')
        json_config[TEMP_KEY] = JSON_FILE_DEFAULTS[TEMP_KEY]
    tank_temp_var.set(temp_dbl)
    print(temp_dbl)

    save_json_config()  # Keep as last


def save_json_config():
    global food_freq_var, food_amt_var, tank_temp_var, \
        json_config, JSON_FILE_DEFAULTS, JSON_FILE_NAME, \
        TEMP_KEY, FREQ_KEY, AMT_KEY

    json_config[FREQ_KEY] = food_freq_var.get() \
        if food_freq_var.get() != '' and food_freq_var.get() is not None else JSON_FILE_DEFAULTS[FREQ_KEY]
    json_config[AMT_KEY] = food_amt_var.get() \
        if food_amt_var.get() != '' and food_amt_var.get() is not None else JSON_FILE_DEFAULTS[AMT_KEY]

    json_config[TEMP_KEY] = tank_temp_var.get()

    json_str = json.dumps(json_config)
    with open(JSON_FILE_NAME, 'w') as file:
        file.write(json_str)
        print('Saved JSON Configuration')


def update_temp_label(value):
    print(value)
    temp_val = tank_temp_var.get()
    temp_formatted = f'{temp_val:2.1f}°F'
    temp_str.set(temp_formatted)


load_json_config()
update_temp_label(None)
# FOOD FREQUENCY

# Food Frequency Label
food_freq_lbl = ttk.Label(frame, text="Food Frequency (# Hours):", padding=LABEL_PADDING, justify=tk.RIGHT)
food_freq_lbl.grid(row=2, column=1, sticky=tk.E)
# Food Frequency Entry
food_freq_ent = ttk.Entry(frame, width=10, textvariable=food_freq_var)
food_freq_ent.grid(row=2, column=2, columnspan=2, sticky=tk.W)

# FOOD AMOUNT

# Food Amount Label
food_amt_lbl = ttk.Label(frame, text='Food Amount (# Units):', padding=LABEL_PADDING, justify=tk.RIGHT)
food_amt_lbl.grid(row=3, column=1, sticky=tk.E)
# Food Amount Entry
food_amt_ent = ttk.Entry(frame, width=4, textvariable=food_amt_var)
food_amt_ent.grid(row=3, column=2, columnspan=2, sticky=tk.W)

# TANK TEMPERATURE

# Tank Temperature Label
tank_temp_lbl = ttk.Label(frame, text='Tank Temperature:', padding=LABEL_PADDING, justify=tk.RIGHT)
tank_temp_lbl.grid(row=4, column=1, sticky=tk.E)
temp_lbl = ttk.Label(frame, textvariable=temp_str, padding=LABEL_PADDING, justify=tk.LEFT)
temp_lbl.grid(row=4, column=2, sticky=tk.W)
# Tank Temperature Slider (Scale)
# Note: Fish usually live in water between 55F and 85F
tank_temp_scl = ttk.Scale(frame, variable=tank_temp_var, from_=68.0, to=93.0, command=update_temp_label)
tank_temp_scl.grid(row=4, column=3, sticky=tk.W)
# Save Changes Button
save_changes_btn = ttk.Button(frame, text='Save Changes', command=save_changes_button, width=50)
save_changes_btn.grid(row=100, column=1, columnspan=4, sticky=tk.W)

#
def test_heater():
    global controller
    controller.heater_toggle(True)
    sleep(60)
    controller.heater_toggle(False)

def test_pixel_strip():
    try:
        from tools.rgb_neopixel import RGBController
        strip = RGBController()
        strip.set_pixel(0, (255, 255, 0))
    except Exception as e:
        print('Could not start up RGB Controller.')

test_heater()
test_pixel_strip()
# Start Program
root.mainloop()
save_json_config()
upload_localcopy_to_google_drive()
