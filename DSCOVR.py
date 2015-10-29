#
# *******************************************************************************
#
# David Marzocca - 25.10.2015
#
# This script downloads a DSCOVR photo from the website to the /photos/ folder
#
# *******************************************************************************

import urllib
import os
import datetime
import re
import calendar
import shutil

# Current working directory
CurrWorkDir = os.getcwd()

# Define the path of where the photos are going to be and their names
DOWNLOADED_IMAGE_PATH = CurrWorkDir + '/photos/'
downloaded_photoname = 'DSCOVR.png'
downloaded_photoname_2 = 'DSCOVR2.png'

# If the folder 'photos' does not exist, it is created
if not os.path.exists(DOWNLOADED_IMAGE_PATH):
        os.makedirs(DOWNLOADED_IMAGE_PATH)


# this function checkes if the url contains an image and, if yes, downloads it
def download_photo(img_url, filename):
    try:
        image_on_web = urllib.urlopen(img_url)
        if image_on_web.headers.maintype == 'image':
            buf = image_on_web.read()
            path = DOWNLOADED_IMAGE_PATH
            file_path = "%s%s" % (path, filename)
            downloaded_image = file(file_path, "wb")
            downloaded_image.write(buf)
            downloaded_image.close()
            image_on_web.close()
        else:
            return False    
    except:
        return False
    return True

today = datetime.datetime.utcnow()

# Starting from today, it will go back in time day by day (up to 1 month)
# until it finds a photo with the time within 2 hours of the present time.
# This allows to avoid some breaks which happen when the satellite does not upload new photos.
for deltaDay in range(0, 30):

	delta_day = datetime.timedelta(days=deltaDay)
	photo_day = today - delta_day

	datetag = str(photo_day.year) + str(photo_day.month).zfill(2) + str(photo_day.day).zfill(2)

	# I open the archive webpage and download it in a buffer
	# This archive contains metadata for all photos taken in a given day

	urlarchive = 'http://epic.gsfc.nasa.gov/api/images.php?date='

	archive_response = urllib.urlopen(urlarchive + datetag)

	buf_archive = archive_response.read()

	# Now with a regular expression I extract the positions of the photos filenames
	list_index_filename = [m.start() for m in re.finditer('epic_1b_', buf_archive)]
	
	# If in that day there are no photos it skips to the previous day
	if len(list_index_filename) == 0:
		continue
	
	# From these positions I get the datecode of each photo: yyyymmddhhmmss
	photo_datecode = []
	for ii in list_index_filename:
		photo_datecode.append(buf_archive[ii + 8: ii + 22])

	# I close the webpage
	archive_response.close()

	# this is the timestamp of the time I'm looking the photo for: time in seconds from a given date
	timestamp_photo_day = (photo_day - datetime.datetime(1970, 1, 1)).total_seconds()

	# I create a list of timestamps from the date codes in the web archive
	rel_photo_timestamp = []
	for datecode in photo_datecode:
		date_time = datetime.datetime(int(datecode[0:4]), int(datecode[4:6]), int(datecode[6:8]), int(datecode[8:10]), int(datecode[10:12]), int(datecode[12:14]))
		rel_photo_timestamp.append( abs((date_time - datetime.datetime(1970, 1, 1)).total_seconds() - timestamp_photo_day ))
	
	# I find the instance in the list closer in time with the present time
	min_deltat_index = rel_photo_timestamp.index(min(rel_photo_timestamp))
	
	# I want the photo to be within 2 hours of the present time, otherwise I search for a previous day
	if min(rel_photo_timestamp) < 2 * 3600:
		break


# End of the For loop.

# This is the datecode of the photo I will download
datecode = photo_datecode[min_deltat_index]


baseurl = 'http://epic.gsfc.nasa.gov/epic-archive/png/epic_1b_'
endurl = '_00.png'
photourl = baseurl + datecode + endurl

# It downloads the photo
download_photo(photourl, downloaded_photoname)

# It makes a second copy. This is only needed for MacOSX in order to correctly refresh the wallpaper
shutil.copy2(DOWNLOADED_IMAGE_PATH + downloaded_photoname, DOWNLOADED_IMAGE_PATH + downloaded_photoname_2)

# The End
raise SystemExit()
