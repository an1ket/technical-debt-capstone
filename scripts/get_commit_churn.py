#Usage: python3 get_bug_commit_ratio_per_file.py <git_repo_path> <output_file>
# python3 get_commit_churn.py /Users/aniketp/Workspace/Capstone/Source/eclipse/eclipse.platform.runtime bug_commit_ratio.csv

__author__ = 'aniket'

from pygit2 import Repository
import sys
import os
import csv
from subprocess import check_output

output_file = "get_commit_churn.csv"
git_folder = ".git/"
csv_header = ['commit', 'commit_ts', 'file_name', 'added_lines', 'deleted_lines', 'commit_debt', 'file_debt']
debt_words = ["hack", "retarded", "at a loss", "stupid", "remove this code", "ugly", "take care", "something's gone wrong", "nuke", "is problematic", "may cause problem", "hacky", "unknown why we ever experience this", "treat this as a soft error", "silly", "workaround for bug", "kludge", "fixme", "this isn't quite right", "trial and error", "give up", "this is wrong", "hang our heads in shame", "temporary solution", "causes issue", "something bad is going on", "cause for issue", "this doesn't look right", "is this next line safe", "this indicates a more fundamental problem", "temporary crutch", "this can be a mess", "this isn't very solid", "this is temporary and will go away", "is this line really safe", "there is a problem", "some fatal error", "something serious is wrong", "don't use this", "get rid of this", "doubt that this would work", "this is bs", "give up and go away", "risk of this blowing up", "just abandon it", "prolly a bug", "probably a bug", "hope everything will work", "toss it", "barf ", "something bad happened", "fix this crap", "yuck", "certainly buggy", "remove me before production", "you can be unhappy now", "this is uncool", "bail out", "it doesn't work yet", "crap", "inconsistency", "abandon all hope", "kaboom"]

def get_commit_churn(repo_path):
    exec_dir = os.getcwd()
    repo = Repository(os.path.join(repo_path, git_folder))
    os.chdir(repo_path)

    debt_commits = get_debt_commits(repo_path) #commit, commit_ts, fiel_path
    file_churn = []

    for commit in repo.walk(repo.head.target):
        print (commit.id)
        curr_commit_ts = int(str(get_unix_timestamp(str(commit.id))).replace("\n", ""))
        debt_commit_flag = [f for f in debt_commits if f['commit'] == str(commit.id)]
        #print (str(debt_commit_flag))
        is_debt_commit = 0
        if debt_commit_flag:
            is_debt_commit = 1

        touched_files = get_touched_files(commit)
        for strFileChurn in touched_files:
            added_lines, deleted_lines, file_name = strFileChurn.split("\t")

            file_commit_flag = [f for f in debt_commits if f['file_path'] == file_name]
            is_file_debt = 0
            if file_commit_flag:
                file_commit_flag = file_commit_flag[0]
                debt_commit_commit_ts = int(file_commit_flag['commit_ts'])
                
                if curr_commit_ts >= debt_commit_commit_ts:
                    is_file_debt = 1

            try:
                file_churn.append({
                    'commit':str(commit.id),
                    'commit_ts':curr_commit_ts,
                    'file_name':file_name,
                    'added_lines':added_lines,
                    'deleted_lines':deleted_lines,
                    'commit_debt':is_debt_commit,
                    'file_debt':is_file_debt,
                    })
            except (AttributeError):
                continue;

    os.chdir(exec_dir)
    with open(output_file, "w", newline='') as output:
        writer = csv.DictWriter(output, csv_header)
        writer.writeheader()
        writer.writerows(file_churn)

def get_unix_timestamp(commit):
    cmd_show_numstat = "git show -s --format=%at " + commit
    commit_stats = check_output(cmd_show_numstat, shell=True).decode("utf-8")
    
    return str(commit_stats)

def get_touched_files(commit):
    # this function returns:
    # "\n
    # <added_lines>\t<deleted_lines>\t<file_name>\n
    # <added_lines>\t<deleted_lines>\t<file_name>"
    cmd_show_numstat = "git show --numstat --format='format:' {0}".format(str(commit.id))
    commit_stats = check_output(cmd_show_numstat, shell=True).decode("utf-8")
    touched_files = []
    for file_stats in commit_stats.split("\n"):
        if len(file_stats.split("\t")) == 3:  # Process only if it's a line with actual data
            touched_files.append(str(file_stats))
    
    return touched_files

def get_debt_commits(repo_path):
    # this function returns a tuple list of all files containing technical debt and their origin

    repo = Repository(os.path.join(repo_path, git_folder))
    file_list = []
    debt_commits_list = []

    for root, dirs, files in os.walk(repo_path):
        for file in files:
            fullpath = os.path.join(root, file)
            if file.endswith('.java'): # TODO
                file_list.append(fullpath)

    for file in file_list:
        with open(file, 'r') as inF:
            line_num = 0
            for line in inF:
                line_num += 1
                if is_debt_line(line):
                    strCommitDetails = get_commit_details(repo, file.replace(repo_path + "/", ""), line_num)
                    strCommitHash = strCommitDetails.split(',')[0]
                    strFilePath = strCommitDetails.split(',')[1]
                    debt_commits_list.append({
                        'commit':strCommitHash,
                        'commit_ts':get_unix_timestamp(strCommitHash),
                        'file_path':strFilePath
                        })
    return debt_commits_list

def get_commit_details(repo, file, line_num):
    blameObj = repo.blame(file)
    blameHunk = blameObj.for_line(line_num)
    return (str(blameHunk.final_commit_id) + "," + file)

def is_debt_line(line):
    return any([word.lower() in line.lower() for word in debt_words])

def main():
    repo_path = sys.argv[1]
    output_file = "commit_churn.csv"
    get_commit_churn(repo_path)

if __name__ == "__main__":
    main()