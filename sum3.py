import openai
import time
from halo import Halo
import textwrap
import yaml
import os
import PyPDF2
from datetime import datetime
import os
import subprocess
from myfunctions import *
import sys
from datetime import datetime
current_date = datetime.now().strftime('%m/%d/%Y %I:%M:%S %p')

current_year = datetime.now().year
current_year_str = str(current_year)

# Commented out the database lookup logic
# contacts_family_csv_string = get_contact_data_as_csv_string('Family')
# contacts_friend_csv_string = get_contact_data_as_csv_string('Friend')

# Do something with the CSV string...
#print(contacts_family_csv_string)
#print(contacts_friend_csv_string)
#sys.exit()

#MyFunctions will pull in anything from sqlite database
print("Before subprocess.call")
ret = subprocess.call(["python", "recentthoughts.py"])
time.sleep(2)

# Format datetime to MM/DD/YYYY H:M:S AM/PM
formatted_datetime = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")

# Rest of the code remains the same...
