import argparse
import subprocess
import re
from datetime import date,timedelta,datetime
from prettytable import PrettyTable
import os
import shutil

def print_report(report_data):
    
    for repo_data in report_data:
        print("Report for: " + repo_data[0])
        t = PrettyTable(['ON DATE', 'TOTAL LINES'])
        for date_results in repo_data[1:]:
            #print(date_results)
            t.add_row(date_results)
        print(t)

def repo_lc_on_date(repo_name,repo_url, date):
    print("Getting LC for " + repo_name + " on " + date + "...")
    os.chdir('/var/tmp')
    folder_name = "sptfy-" + repo_name + "-" + date.replace(" ", "")
    #cleanup the tmmp folder
    shutil.rmtree('/var/tmp/' + folder_name, ignore_errors=True)
    #clone
    proc = subprocess.Popen(['git', 'clone', repo_url, folder_name], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    output = proc.stdout.read()
    output=output.rstrip().decode('UTF-8')
    print("Repo updated")
    #get commit hash
    os.chdir('/var/tmp/'+folder_name)
    proc = subprocess.Popen(['git', 'rev-parse', "--until=\"" + date + "\""], stdout=subprocess.PIPE)
    output = proc.stdout.read()
    output=output.rstrip().decode('UTF-8')
    #print(output)
    proc = subprocess.Popen(['git', 'rev-list', '-1', output, "master"], stdout=subprocess.PIPE)
    output = proc.stdout.read()
    output=output.rstrip().decode('UTF-8')
    #print(output)
    #reset repo to that commit
    proc = subprocess.Popen(['git', 'reset', '--hard', output], stdout=subprocess.PIPE)
    output = proc.stdout.read()
    output=output.rstrip().decode('UTF-8')
    #print(output)
    #get cloc data on this repo
    proc = subprocess.Popen(['cloc', '.' ,'--exclude-ext=html'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    for output in proc.stdout.readlines():
        #sections = str(line).split(\\9)
        str_line = output.strip().decode('UTF-8')
        #print(str_line)
        if 'SUM' in str_line:
            splitted = re.split('    ', str_line)
            #print(splitted)
            lc = splitted[-1]

    #cleanup the tmmp folder
    shutil.rmtree('/var/tmp/' + folder_name, ignore_errors=True)

    # lc on this date found! return it
    return lc

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dates_from_file", help="optinal file with list of date ranges" , type=str)
    parser.add_argument("--repos_from_file", help="names of file with all repos folders" , type=str)
    args = parser.parse_args()

    repos = []
    if args.dates_from_file:
        f=open(args.repos_from_file,'r')
        while True:
            line = f.readline()
            line = line.rstrip()
            if not line: break
            x = re.split(',', line)
            repos.append(x)

    dates = []
    if args.dates_from_file:
        f=open(args.dates_from_file,'r')
        while True:
            line = f.readline()
            line = line.rstrip()
            if not line: break
            x = re.split(',', line)
            dates.append(x[1])

    report_data = []
    for repo in repos:
        repo_data = []
        repo_data.append(repo[0])
        for date in dates:
            date_data = []
            date_data.append(date)
            date_data.append(repo_lc_on_date(repo[0], repo[1], date))
            repo_data.append(date_data)
        report_data.append(repo_data)
        print_report(report_data)

    #print(report_data)
    print_report(report_data)
    #cleanup()
    