import argparse
import subprocess
import re
from datetime import date,timedelta,datetime
from prettytable import PrettyTable
import logging


def query_on_day(from_date, to_date):
    print("Fetchig stats between " + from_date + " and " + to_date + "...")

    results = []
    results.append(str(from_date))
    results.append(str(to_date))

    # Calculate number of workingdays in period
    start_date = datetime.strptime(from_date, '%b %d %Y')
    end_date= datetime.strptime(to_date, '%b %d %Y')
    daygenerator = (start_date + timedelta(x + 1) for x in range((end_date - start_date).days))
    working_days = sum(1 for day in daygenerator if day.weekday() < 5)
    logging.debug("Working Days: " + str(working_days))
    results.append(str(working_days))

    # Get total number of committer
    cmd = ["git", "shortlog", "-sne",  "--since", from_date, "--until", to_date]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    total_committers = 0
    total_commits = 0
    for line in proc.stdout.readlines():
        str_line = str(line).strip()
        logging.debug(str_line)
        splitted = re.split('\\\|, |     |   |  ', str_line)
        if isinstance(splitted, list):
            logging.debug(splitted)
            committer_name = splitted[2].strip()
            if "tutter" not in committer_name and "Teamcity" not in committer_name:
                committer_commits = int(splitted[1].strip()) 
                total_committers += 1
                total_commits += committer_commits

    logging.debug("Total committers: " + str(total_committers))
    logging.debug("Total commits: " + str(total_commits))
    results.append(str(total_committers))
    results.append(str(total_commits))
    results.append("%.2f" % (total_commits/working_days if working_days else 0))
    results.append("%.2f" % (total_commits/working_days/total_committers if working_days and total_committers else 0))

    # Get total number of lines changed during this period
    cmd = ["git", "log", "--since", from_date, "--until", to_date, "--oneline", "--shortstat"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    insertions = 0
    deletions = 0
    for line in proc.stdout.readlines():
        str_line = str(line).strip()
        logging.debug(str_line)
        if "insertions(" in str_line:
            matches = re.findall('(\d+) insertions', str_line)
            if len(matches) > 0:
                logging.debug(matches[0])
                insertions+=int(matches[0])
        if "deletions(" in str_line:
            matches = re.findall('(\d+) deletions', str_line)
            if len(matches) > 0:
                logging.debug(matches[0])
                deletions+=int(matches[0])

    logging.debug("Total additions: " + str(insertions))
    logging.debug("Total deletions: " + str(deletions))
    results.append(str(insertions))
    results.append("%.2f" % (insertions/working_days))
    results.append("%.2f" % (insertions/working_days/total_committers if working_days and total_committers else 0))
    results.append(str(deletions))
    results.append("%.2f" % (deletions/working_days))
    results.append("%.2f" % (deletions/working_days/total_committers if working_days and total_committers else 0))

    # Done!
    return results

def print_report(report_data):

    print("\n")
    t = PrettyTable(['FROM', 'TO', 'WORKING DAYS', 'COMMITTERS','TOTAL COMMITS', 'COMMITS/DAY', 'COMMITS/DAY/COMMITTER', 'TOTAL INS', 'INS/DAY', 'INS/DAY/COMMITER', 'TOTAL DEL', 'DEL/DAY', 'DEL/DAY/COMMITER'])
    for range_results in report_data:
        t.add_row(range_results)
    print(t)

if __name__ == "__main__":
    # Set logging level
    logging.basicConfig(level=logging.INFO)
    # Get arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--from_date", help="start date for stats (format \"Oct 1 2017\")" , type=str)
    parser.add_argument("--to_date", help="end date for stats (format \"Nov 1 2017\")" , type=str)
    parser.add_argument("--dates_from_file", help="optinal file with list of date ranges" , type=str)
    args = parser.parse_args()
    # Fetch stats for the current repo
    report_data = []
    if args.dates_from_file:
        f=open(args.dates_from_file,'r')
        while True:
            line = f.readline()
            line = line.rstrip()
            if not line: break
            dates = re.split(',', line)
            range_data = query_on_day(dates[0], dates[1])
            report_data.append(range_data)
        print_report(report_data)
    else:
        range_data = query_on_day(args.from_date, args.to_date)
        report_data.append(range_data)
        print_report(report_data)