# MAIN DIFFERENCES TO main.py
#   do not process ip addresses or geo information
#   just print to stdout
# MAIN FEATURE HERE:
#   print log file contents continuously, similar to fluent.d
#   especially useful in a Kubernetes environemnt

import os
import sys
import argparse as ap

class MyParser(ap.ArgumentParser):
    def error(self, message):
        print('DEBUG: error: %s\n' % message)
        self.print_help()
        sys.exit(2)


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
        print('DEBUG: Log file has been rotated, reset last processed line number')
        last_processed_line = 0

    return last_processed_line


def process_log(log_file, last_line_file, args):
    last_processed_line = get_last_processed_line(log_file, last_line_file)

    processed_line_count = 0
    if line_count(log_file) >= last_processed_line:
        with open(log_file, 'r') as file:
            # Skip lines until reaching the last processed line
            try:
                for _ in range(last_processed_line):
                    next(file)
            except:
                print('DEBUG: Error while jumping to last_processed_line, reset it\n')
                last_processed_line = 0

            # Process remaining lines
            for line_number, line in enumerate(file, start=last_processed_line + 1):
                print(f"{log_file}: {line.strip()}")

                processed_line_count += 1
                last_processed_line = line_number

    if processed_line_count != 0:
        print(f'DEBUG: Processed remaining {processed_line_count} lines from {log_file}:{last_processed_line}')
    
    # Write the last processed line number to the file
    with open(last_line_file, 'w') as f:
        f.write(str(last_processed_line))


def handle_args():
    p = MyParser(description="Configuration", formatter_class=ap.ArgumentDefaultsHelpFormatter)
    p.add_argument("-f", "--sourcefiles", action="append", help="File(s) to read from", required=True)

    if len(sys.argv) == 1:
        p.print_help()
        sys.exit(1)

    args = p.parse_args()

    return args


if __name__ == '__main__':
    args = handle_args()

    LOG_FILES = args.sourcefiles

    # Path to the file storing the last processed line number for each log file
    LAST_LINE_FILES = ["%s.last_line" % filename for filename in LOG_FILES]

    # Process each Apache access log file and save geolocated data to the output file
    for log_file, last_line_file in zip(LOG_FILES, LAST_LINE_FILES):
        if os.path.isfile(log_file):
            process_log(log_file, last_line_file, args)
