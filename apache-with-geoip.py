import os
import sys
import re
import geoip2.database

# Path to the MaxMind GeoIP2 database file
DATABASE_FILE = 'geoip-db/GeoLite2-City.mmdb'

print_unknown_ips = False

# Initialize the GeoIP2 reader
reader = geoip2.database.Reader(DATABASE_FILE)

# List of paths to Apache access log files
LOG_FILES = [
    'sample-logs/access.log',
    'sample-logs/other_vhosts_access.log',
]

# Path to the file storing the last processed line number for each log file
LAST_LINE_FILES = [filename.replace('.log', '.last_line') for filename in LOG_FILES]

def exit_if_file_missing(filename):
    if not os.path.isfile(filename):
        sys.stderr.write(f'Houston, we have a problem, {filename} is missing\n')
        sys.exit(1)

# Regular expressions for extracting IP addresses from log lines of different formats
IP_REGEX_ACCESS_LOG = r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
IP_REGEX_VHOST_LOG = r'^\S+ (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'

def get_geolocation(ip_address):
    try:
        # Perform GeoIP lookup for the IP address
        response = reader.city(ip_address)
        country = response.country.name
        city = response.city.name
        latitude = response.location.latitude
        longitude = response.location.longitude
        return country, city, latitude, longitude
    except Exception as e:
        if print_unknown_ips:
            sys.stderr.write(f"Error: {e}\n")
        return None, None, None, None

def process_access_log(log_file, last_line_file, ip_regex):
    last_processed_line = 0
    
    # Read the last processed line number from the file
    try:
        with open(last_line_file, 'r') as f:
            last_processed_line = int(f.read())
    except FileNotFoundError:
        pass
    
    # Check if the log file has been rotated (inode number changed)
    current_inode = os.stat(log_file).st_ino
    if last_processed_line > 0 and last_processed_line > current_inode:
        # Log file has been rotated, reset last processed line number
        last_processed_line = 0
    
    with open(log_file, 'r') as file:
        # Skip lines until reaching the last processed line
        for _ in range(last_processed_line):
            next(file)
        
        # Process remaining lines
        for line_number, line in enumerate(file, start=1):
            match = re.match(ip_regex, line)
            if match:
                ip_address = match.group(1)
            else:
                if print_unknown_ips:
                    sys.stderr.write(f"Skipping log line {line_number} - No IP address found\n")
                continue
            
            # Perform GeoIP lookup
            country, city, latitude, longitude = get_geolocation(ip_address)
            
            # Write the original log line and geolocation information to the output file
            if country and city:
                print(f"{line.strip()} country:\"{country}\" city:\"{city}\" lat:{latitude} lng:{longitude}")
            else:
                if print_unknown_ips:
                    sys.stderr.write(f"Skipping log line {line_number} - Geolocation not found\n")
                
            # Update last processed line number
            last_processed_line = line_number
    
    # Write the last processed line number to the file
    with open(last_line_file, 'w') as f:
        f.write(str(last_processed_line))

[exit_if_file_missing(filename) for filename in LOG_FILES]
exit_if_file_missing(DATABASE_FILE)

# Process each Apache access log file and save geolocated data to the output file
for log_file, last_line_file in zip(LOG_FILES, LAST_LINE_FILES):
    if 'vhost' in log_file:  # Check if it's a virtual host log file
        ip_regex = IP_REGEX_VHOST_LOG
    else:
        ip_regex = IP_REGEX_ACCESS_LOG
    process_access_log(log_file, last_line_file, ip_regex)

# Close the GeoIP2 reader
reader.close()
