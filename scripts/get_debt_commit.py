#Usage: python3 get_debt_commit.py <git_repo_path> <git_repo_path> <git_repo_path> 
#python3 get_debt_commit.py /Users/aniketp/Workspace/Capstone/Source/eclipse/eclipse.platform.runtime /Users/aniketp/Workspace/Capstone/Source/eclipse/eclipse.platform.ui
#git blame -L4620,+1 <file path>

__author__ = 'aniket'

from pygit2 import Repository
import sys
import os
import csv

git_log_csv = []
git_folder = ".git/"
debt_words = ["hack", "retarded", "at a loss", "stupid", "remove this code", "ugly", "take care", "something's gone wrong", "nuke", "is problematic", "may cause problem", "hacky", "unknown why we ever experience this", "treat this as a soft error", "silly", "workaround for bug", "kludge", "fixme", "this isn't quite right", "trial and error", "give up", "this is wrong", "hang our heads in shame", "temporary solution", "causes issue", "something bad is going on", "cause for issue", "this doesn't look right", "is this next line safe", "this indicates a more fundamental problem", "temporary crutch", "this can be a mess", "this isn't very solid", "this is temporary and will go away", "is this line really safe", "there is a problem", "some fatal error", "something serious is wrong", "don't use this", "get rid of this", "doubt that this would work", "this is bs", "give up and go away", "risk of this blowing up", "just abandon it", "prolly a bug", "probably a bug", "hope everything will work", "toss it", "barf ", "something bad happened", "fix this crap", "yuck", "certainly buggy", "remove me before production", "you can be unhappy now", "this is uncool", "bail out", "it doesn't work yet", "crap", "inconsistency", "abandon all hope", "kaboom"]

def is_debt_line(line):
    return any([word.lower() in line.lower() for word in debt_words])

def get_debt_commit(repo, file, line_num):
    #print (file)
    #print (os.getcwd())
    blameObj = repo.blame(file)
    blameHunk = blameObj.for_line(line_num)
    print(str(blameHunk.final_commit_id)[:7] + "\t" + file)

def get_file_list(repo_path):
    repo = Repository(os.path.join(repo_path, git_folder))
    file_list = []

    for root, dirs, files in os.walk(repo_path):
        for file in files:
            fullpath = os.path.join(root, file)
            if file.endswith('.java'):
                file_list.append(fullpath)

    for file in file_list:
        with open(file, 'r') as inF:
            line_num = 0
            for line in inF:
                line_num += 1
                if is_debt_line(line):
                    get_debt_commit(repo, file.replace(repo_path + "/", ""), line_num)
                    #print (str(line_num) + " " + file)

def main():
    exec_dir = os.getcwd()
    for repo_path in sys.argv[1:]:
        print ("*** repo " + repo_path + " ***")
        get_file_list(repo_path)

if __name__ == "__main__":
    main()