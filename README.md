# apache-with-geoip
Ingest and enrich apache logs with geoip information (country, city, latitude, longitude), then add it to another log.

## Setup on the server
- Get the GeoLite-City.mmdb from MaxMind GeoIP and store it to the `geoip-db` folder.
- install requirements as root `python3 -m pip install -r requirements.txt`
- add this to roots crontab: `* * * * * /usr/bin/python3 /YOUR/PATH/apache-with-geoip/apache-with-geoip.py`
- to run it more often than once a minute (eg every 10 seconds), you could use this: `*/1 * * * * /YOUR/PATH/apache-with-geoip/runEvery.sh 10 /usr/bin/python3 /YOUR/PATH/apache-with-geoip/apache-with-geoip.py`
- watch all_with_geoip.log grow with added geo data!

## TO DO
- make paths configurable

## Simulate behaviour (manual testing)
prepare these files:
- other_vhosts_access.log <- should be empty
- other_vhosts_access.orig.log <- should contain some log lines (at least 100 for more fun)

run this in one window:

	./log_faker.sh other_vhosts_access.orig.log other_vhosts_access.log

and this in another

	while [ 1 ]; do
        python3 apache-with-geoip.py
	    sleep 3
	done

Then watch the OUT_FILE grow with added geo data!
