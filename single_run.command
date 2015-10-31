#
# This script creates a cron job which runs the python script every 30 minutes.
#
#
# You can see how many jobs are currently scheduled from inside of cron by typing the following command:
# crontab -l
#

cd `dirname $0`

ThisFolder="$(pwd)"

python DSCOVR.py

#(crontab -l 2>/dev/null; echo " */30 * * * * cd "$ThisFolder"/; python DSCOVR.py >/dev/null 2>&1") | crontab -

