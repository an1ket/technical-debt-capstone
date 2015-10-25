#Usage: python3 get_churn_per_commit.py <git_repo_path> <output_file>
#python3 get_churn_per_commit.py /Users/aniketp/Workspace/Capstone/Source/eclipse/eclipse.platform.runtime churn_eclipse.csv

__author__ = 'aniket'

from pygit2 import Repository
import sys
import os
import csv
from subprocess import check_output

default_output_file = "bug_commit_ratio.csv"
git_folder = ".git/"

csv_header = ['file_name', 'hash', 'lines_added', 'lines_removed']

def get_blame_test():
    git_repo = "/Users/aniketp/Workspace/Capstone/Source/eclipse/eclipse.platform.runtime"
    sample_file = "bundles/org.eclipse.core.jobs/src/org/eclipse/core/internal/jobs/JobManager.java"
    exec_dir = os.getcwd()
    repo = Repository(os.path.join(git_repo, git_folder))
    os.chdir(git_repo)
    
    blameObj = repo.blame(sample_file, min_line=1, max_line=20)

def get_touched_files(commit):
    # This git command returns:
    # "\n
    # <added_lines>\t<deleted_lines>\t<file_name>\n
    # <added_lines>\t<deleted_lines>\t<file_name>"
    cmd_show_numstat = "git show --numstat --format='format:' {0}".format(str(commit.id))
    commit_stats = check_output(cmd_show_numstat, shell=True).decode("utf-8")

    touched_files = []

    for file_stats in commit_stats.split("\n"):
        if len(file_stats.split("\t")) == 3:  # Process only if it's a line with actual data
            added_lines, deleted_lines, file_name = file_stats.split("\t")
            #touched_files.append(file_name)
            print(file_name + " +" +added_lines+ " -"+deleted_lines)
            touched_files.append({
                'file_name':file_name,
                'hash':commit,
                'lines_added':added_lines,
                'lines_removed':deleted_lines
                })

    return touched_files


def get_bug_commit_ratio_per_file(git_folder = ".git/", output_file):
    result = []
    exec_dir = os.getcwd()
    repo = Repository(os.path.join(git_repo, git_folder))

    os.chdir(git_repo)

    for commit in repo.walk(repo.head.target):
        touched_files = get_touched_files(commit)

        for file in touched_files:
            file_data = [f for f in result if f['file_name'] == file]

            if file_data:
                file_data = file_data[0]
                file_data['commit_num'] += 1
                if bug_related:
                    file_data['bug_commit_num'] += 1
            else:
                result.append({'file_name': file,
                               'commit_num': 1,
                               'bug_commit_num': 1 if bug_related else 0})

    os.chdir(exec_dir)

    for entry in result:
        entry['bug_commit_ratio'] = entry['bug_commit_num'] / entry['commit_num']

    with open(output_file, "w", newline='') as output:
        writer = csv.DictWriter(output, csv_header)
        writer.writeheader()
        writer.writerows(result)

def get_churn_per_commit(git_repo, output_file):
    touched_files = []
    exec_dir = os.getcwd()
    repo = Repository(os.path.join(git_repo, git_folder))
    os.chdir(git_repo)

    for commit in repo.walk(repo.head.target):
        touched_files = get_touched_files(commit)

    with open(output_file, "w", newline='') as output:
        writer = csv.DictWriter(output, csv_header)
        writer.writeheader()
        writer.writerows(touched_files)


def main():
    repo_path = sys.argv[1]
    output_file = default_output_file

    if len(sys.argv) > 2:
        output_file = sys.argv[2]

    get_churn_per_commit(repo_path, output_file)


if __name__ == "__main__":
    main()