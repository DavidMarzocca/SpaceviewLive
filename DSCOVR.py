#
# *******************************************************************************
#
# David Marzocca - 25.10.2015
#
# This script downloads a DSCOVR photo from the website to the /photos/ folder
#
# *******************************************************************************


# ************** Libraries and definitions *******************

import os
import requests
import datetime
import shutil
import json
from itertools import islice

# This function adds a line to the beginning of a file, keeping a max of 100 lines
# If there is no file it creates it.
def write_on_log(filename, line):
	if os.path.exists(filename):
		with open(filename, 'r+') as f:
			content = list(islice(f, 99))
			f.seek(0, 0)
			f.write(line.rstrip('\r\n') + '\n')
			for oldline in content:
				f.write(oldline)
			f.close()
	else:
		with open(filename, 'w') as f:
			f.write(line)
			f.close()



# ************** Beginning of the script *******************


# Define the path of where the photos are going to be and their names
download_dir = 'photos'
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

found_photo = False
max_days_back = 5
now = datetime.datetime.utcnow()

for delta_days in range(max_days_back):
    # Starting from today, it will go back in time day by day (up to 100 days)
    # until it finds a photo with the time within 2 hours of the present time.
    # This allows to avoid some breaks which happen when the satellite does not upload new photos.
    photo_date = now - datetime.timedelta(days=delta_days)
    photo_date_str = photo_date.strftime('%Y%m%d')

    # I open the archive webpage and download it in a buffer
    # This archive contains metadata for all photos taken in a given day
    url_archive = f'https://epic.gsfc.nasa.gov/api/natural/date/{photo_date_str}'
    # print(url_archive)
    
    try:
        archive_response = requests.get(url_archive)
        archive_response.raise_for_status()
        metadata = archive_response.json()
        
    except requests.exceptions.HTTPError:
        continue

    # If in that day there are no photos it skips to the previous day
    if len(metadata) == 0:
        continue

    # Find the closest photo to now, within 2 hours.
    min_deltat = datetime.timedelta.max
    
    for photo in metadata:

        # Extract hour, minute, and second information from photo timestamp
        photo_time = datetime.datetime.fromisoformat(photo['date']).time()
        
        # Convert photo_time and current time to datetime objects
        current_datetime = datetime.datetime.now()
        photo_datetime = datetime.datetime.combine(current_datetime.date(), photo_time)

        # Calculate the time difference between the current time and photo time
        delta_t = abs(current_datetime - photo_datetime)

        if delta_t < min_deltat:
            min_deltat = delta_t
            closest_photo = photo

    # I want the photo to be within 2 hours of the present time, otherwise I search for a previous day
    if min_deltat > datetime.timedelta(hours=2):
        continue

    found_photo = True
    closest_photo_str = json.dumps(closest_photo)

    
    print('I found a photo')
    
    break

# If it found a photo it will download it and print the date tag on the log file
if found_photo:
    
    # Download the photo and save it in the download directory
    timestamp = closest_photo_str[16:30]
    photo_url = f'http://epic.gsfc.nasa.gov/epic-archive/png/epic_1b_{timestamp}.png'
    
    #photo_filename = os.path.join(download_dir, os.path.basename(photo_url))
    photo_filename = os.path.join(download_dir, 'DSCOVR.png')
    response = requests.get(photo_url, stream=True)
    
    with open(photo_filename, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response
    
    # Create a copy of the downloaded photo with a different filename
    copy_filename = os.path.join(download_dir, 'DSCOVR2.png')
    shutil.copy(photo_filename, copy_filename)


    to_print = 'Script time = ' + now.strftime("%Y-%m-%d %H:%M:%S") + ' GMT. Photo time = ' + closest_photo['date'] + '. URL: ' + photo_url
    
        
else:
	to_print = 'No photo found within the last 100 days.'
	print('No photo found within the last 100 days.')

    
print(to_print)

# Write on the log.txt file
write_on_log('log.txt', to_print)

# The End
raise SystemExit()
