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


# I want it to download two-days-ago photo from the same hour we are in
# The reason for the two days is because the photos are uploaded
# with 24-36 hours of delay from the time they are taken
today = datetime.datetime.utcnow()
two_day = datetime.timedelta(days=2)
yesterday = today - two_day

datetag = str(yesterday.year) + str(yesterday.month).zfill(2) + str(yesterday.day).zfill(2)


# I open the archive webpage and download it in a buffer
# This archive contains metadata for all photos taken in a given day

urlarchive = 'http://epic.gsfc.nasa.gov/api/images.php?date='

archive_response = urllib.urlopen(urlarchive + datetag)

buf_archive = archive_response.read()

# Now with a regular expression I extract the positions of the photos filenames
list_index_filename = [m.start() for m in re.finditer('epic_1b_', buf_archive)]

# From these positions I get the datecode of each photo: yyyymmddhhmmss
photo_datecode = []
for ii in list_index_filename:
	photo_datecode.append(buf_archive[ii + 8: ii + 22])

# I close the webpage
archive_response.close()

# this is the present timestamp: time in seconds from a given date
timestamp_yest = (yesterday - datetime.datetime(1970, 1, 1)).total_seconds()

# I create a list of timestamps from the date codes in the web archive
rel_photo_timestamp = []
for datecode in photo_datecode:
	date_time = datetime.datetime(int(datecode[0:4]), int(datecode[4:6]), int(datecode[6:8]), int(datecode[8:10]), int(datecode[10:12]), int(datecode[12:14]))
	rel_photo_timestamp.append( abs((date_time - datetime.datetime(1970, 1, 1)).total_seconds() - timestamp_yest ))
	
# I find the instance in the list closer in time with the present time
min_deltat_index = rel_photo_timestamp.index(min(rel_photo_timestamp))

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

