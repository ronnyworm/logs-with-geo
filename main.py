import os
import sys
import re
import geoip2.database
import argparse as ap
import time

# Regular expressions for extracting IP addresses from log lines of different formats
IP_REGEX_ACCESS_LOG = r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
IP_REGEX_VHOST_LOG = r'^\S+ (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'

print_unknown_ips_to_stderr = True

class MyParser(ap.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


def exit_if_file_missing(filename):
    if not os.path.isfile(filename):
        sys.stderr.write(f'Houston, we have a problem, {filename} is missing\n')
        sys.exit(1)


def print_to(outfile, text):
    f = open(outfile, 'a', encoding='utf-8')

    f.write(text + "\n")
    f.close()


def get_geolocation(geoip2_reader, ip_address):
    try:
        # Perform GeoIP lookup for the IP address
        response = geoip2_reader.city(ip_address)
        country = response.country.name
        city = response.city.name
        latitude = response.location.latitude
        longitude = response.location.longitude
        return country, city, latitude, longitude
    except Exception as e:
        if print_unknown_ips_to_stderr:
            sys.stderr.write(f"Error: {e}\n")
        return None, None, None, None


def line_count(filename):
    lines = 0
    with open(filename, 'r') as fp:
        lines = len(fp.readlines())
    return lines


def get_last_processed_line(log_file, last_line_file):
    last_processed_line = 0

    # Read the last processed line number from the file
    try:
        with open(last_line_file, 'r') as f:
            last_processed_line = int(f.read())
    except (FileNotFoundError, ValueError):
        pass
    
    # Check if the log file has been rotated
    if last_processed_line > 0 and last_processed_line > line_count(log_file):
        sys.stderr.write('Log file has been rotated, reset last processed line number')
        last_processed_line = 0

    return last_processed_line


def process_access_log(log_file, last_line_file, ip_regex, args, geoip2_reader):
    last_processed_line = get_last_processed_line(log_file, last_line_file)

    processed_line_count = 0
    if line_count(log_file) >= last_processed_line:
        with open(log_file, 'r') as file:
            # Skip lines until reaching the last processed line
            try:
                for _ in range(last_processed_line):
                    next(file)
            except:
                sys.stderr.write('Error while jumping to last_processed_line, reset it\n')
                last_processed_line = 0

            # Process remaining lines
            for line_number, line in enumerate(file, start=last_processed_line + 1):
                process_single_line(line_number, line, ip_regex, args, geoip2_reader)

                processed_line_count += 1
                last_processed_line = line_number

    print(f'Processed remaining {processed_line_count} lines from {log_file}:{last_processed_line}')
    
    # Write the last processed line number to the file
    with open(last_line_file, 'w') as f:
        f.write(str(last_processed_line))


def process_single_line(line_number, line, ip_regex, args, geoip2_reader):
    match = re.match(ip_regex, line)
    if match:
        ip_address = match.group(1)

        # Perform GeoIP lookup
        country, city, latitude, longitude = get_geolocation(geoip2_reader, ip_address)
        
        # Write the original log line and geolocation information to the output file
        if country and city:
            print_to(args.outfile, f"{line.strip()} country:\"{country}\" city:\"{city}\" lat:{latitude} lng:{longitude}")
        else:
            if print_unknown_ips_to_stderr:
                sys.stderr.write(f"Log line {line_number} - Geolocation for {ip_address} not found\n")

            if args.logunresolved == 1:
                print_to(args.outfile, f"{line.strip()} country:\"\" city:\"\" lat: lng:")

    else:
        if print_unknown_ips_to_stderr:
            sys.stderr.write(f"Log line {line_number} - No IP address found\n")

        if args.logunresolved == 1:
            print_to(args.outfile, f"{line.strip()} country:\"\" city:\"\" lat: lng:")


def handle_args():
    p = MyParser(description="Configuration", formatter_class=ap.ArgumentDefaultsHelpFormatter)
    p.add_argument("-o", "--outfile", default='/var/log/apache2/with_geoip.log', help="Path to file that stores the enriched logs", required=True)
    p.add_argument("-f", "--sourcefiles", action="append", help="File(s) to read from", required=True)
    p.add_argument("-t", "--type", help="Log file type (guessing from outfile by default)")
    p.add_argument("-i", "--interval", type=int, default=5, help="Interval (seconds) in which to process the logfiles; if -1 is given, it will process just once")
    p.add_argument("--logunresolved", type=int, default=1, help="Also print to outfile if no geo info could be retrieved")

    if len(sys.argv) == 1:
        p.print_help()
        sys.exit(1)

    args = p.parse_args()

    return args


def main(how_often=-1):
    args = handle_args()

    SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
    DATABASE_FILE = SCRIPT_PATH + '/geoip-db/GeoLite2-City.mmdb' # MaxMind GeoIP2 database

    LOG_FILES = args.sourcefiles

    if args.type == "":
        if "apache" in args.outfile:
            args.type = "apache"
        elif "nginx" in args.outfile:
            args.type = "nginx"

    # Path to the file storing the last processed line number for each log file
    LAST_LINE_FILES = [filename.replace('.log', '.last_line') for filename in LOG_FILES]

    [exit_if_file_missing(filename) for filename in LOG_FILES]
    exit_if_file_missing(DATABASE_FILE)

    geoip2_reader = geoip2.database.Reader(DATABASE_FILE)

    # Process each log file and save geolocated data to the output file
    try:
        count = 0
        while how_often == -1 or count < how_often:
            for log_file, last_line_file in zip(LOG_FILES, LAST_LINE_FILES):
                if 'vhost' in log_file:  # Check if it's a virtual host log file
                    ip_regex = IP_REGEX_VHOST_LOG
                else:
                    ip_regex = IP_REGEX_ACCESS_LOG
                process_access_log(log_file, last_line_file, ip_regex, args, geoip2_reader)
            if args.interval == -1:
                break
            time.sleep(args.interval)
            count += 1

    finally:
        geoip2_reader.close()


if __name__ == '__main__':
    main()
