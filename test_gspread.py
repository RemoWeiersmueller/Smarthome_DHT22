import gspread
import os

# Get absolute path to credentials
home_dir = os.path.expanduser('~')
creds_path = os.path.join(home_dir, '.config', 'gspread', 'credentials.json')

gc = gspread.oauth(
    credentials_filename=creds_path,
    authorized_user_filename=os.path.join(home_dir, '.config', 'gspread', 'authorized_user.json')
)

# Try to open your spreadsheet (replace with your spreadsheet name)
sh = gc.open("DHT22")
print(sh.sheet1.get('A1'))