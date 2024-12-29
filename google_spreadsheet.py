# SPDX-FileCopyrightText: 2019 Tony DiCola for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
Google Spreadsheet DHT Sensor Data-logging Example

Copyright (c) 2014 Adafruit Industries
Author: Tony DiCola
Modified by: Brent Rubell for Adafruit Industries

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import sys
import time
import datetime
import board
import adafruit_dht
import gspread
import os

# Type of sensor, can be `adafruit_dht.DHT11` or `adafruit_dht.DHT22`.
# For the AM2302, use the `adafruit_dht.DHT22` class.
DHT_TYPE = adafruit_dht.DHT22

# Example of sensor connected to Raspberry Pi Pin 23
DHT_PIN = board.D4

# Initialize the dht device, with data pin connected to:
dhtDevice = DHT_TYPE(DHT_PIN)

# Path to credentials files
home_dir = os.path.expanduser('~')
creds_path = os.path.join(home_dir, '.config', 'gspread', 'credentials.json')
authorized_user_path = os.path.join(home_dir, '.config', 'gspread', 'authorized_user.json')

# Authenticate using gspread.oauth()
gc = gspread.oauth(
    credentials_filename=creds_path,
    authorized_user_filename=authorized_user_path
)

# Google Docs spreadsheet name.
GDOCS_SPREADSHEET_NAME = 'DHT22'

# How long to wait (in seconds) between measurements.
FREQUENCY_SECONDS = 30


def login_open_sheet(spreadsheet):
    """Connect to Google Docs spreadsheet and return the first worksheet."""
    try:
        worksheet = gc.open(spreadsheet).sheet1  # pylint: disable=redefined-outer-name
        return worksheet
    except Exception as ex:
        print('Unable to login and get spreadsheet.  Check OAuth credentials, spreadsheet name, \
        and make sure spreadsheet is shared to the client_email address in the OAuth .json file!')
        print('Google sheet login failed with error:', ex)
        sys.exit(1)


print('Logging sensor measurements to {0} every {1} seconds.'.format(GDOCS_SPREADSHEET_NAME, FREQUENCY_SECONDS))
print('Press Ctrl-C to quit.')

# Initialize worksheet
worksheet = login_open_sheet(GDOCS_SPREADSHEET_NAME)

while True:
    try:
        # Attempt to get sensor reading.
        temp = dhtDevice.temperature
        humidity = dhtDevice.humidity

        # Skip to the next reading if a valid measurement couldn't be taken.
        if humidity is None or temp is None:
            time.sleep(2)
            continue

        print('Temperature: {0:0.1f} C'.format(temp))
        print('Humidity:    {0:0.1f} %'.format(humidity))

        # Format the current timestamp to MM/DD/YYYY HH:MM:SS
        timestamp = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')

        # Append the data in the spreadsheet, including a formatted timestamp
        try:
            worksheet.append_row((timestamp, temp, humidity))
        except Exception as ex:
            # Error appending data, most likely because credentials are stale.
            # Null out the worksheet so a login is performed at the top of the loop.
            print('Append error, logging in again:', ex)
            worksheet = None
            time.sleep(FREQUENCY_SECONDS)
            continue

        # Wait before continuing
        print('Wrote a row to {0}'.format(GDOCS_SPREADSHEET_NAME))
        time.sleep(FREQUENCY_SECONDS)

    except RuntimeError as e:
        # Handle checksum errors and retry
        print("RuntimeError:", e)
        time.sleep(2)
        continue