#!/usr/bin/env python3
import subprocess
import os

from pathlib import Path

# Custom colors :) 
from colorizer import red, yellow, green, blue

"""
Run this inside a git repo to check the latest commit, and find all the files that contain
"test" or "tests" in their filepaths. 

Use case: 
When I work on a new feature etc, I usually include my business logic changes and test changes
in a single commit. When getting peer review, sometimes I have to change the business logic. Once I do, 
I add the changes back to the original commit with git commit --amend. I should be able to validate
my commit still passes the tests before I submit a new version to be reviewed. It should also have no
external dependencies since some developers cannot download stuff via PIP in their development enviornments.

Setup:
You should have a '.testme' folder inside the base of the repo with an executable file called
'test_runner' which takes the absolute path of a test as an arg, and runs the test, returning 0 if successful.

Add the folder this file is in to your path, e.g. 

export PATH="$PATH:$HOME/Tools/TestMe/testme"

Bugs:
This probably won't work if the latest commit _removes_ tests, as it will think the tests are there are try
to run them. I wouldn't put this as a post-commit hook or anything unless this gets fixed.

This has 0 external dependencies :) Useable anywhere you can download python3

- Noah 
"""

def run_cli(command):
    try:
        output = subprocess.run(command.split(), capture_output=True)
    except:
        # In python 3.6>=, we need to use the pipes instead
        output = subprocess.run(command.split, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return output

def get_toplevel_repo():
    """Returns the toplevel git repo directory"""
    command = "git rev-parse --show-toplevel"
    result = run_cli(command)
    output = result.stdout.decode("utf-8").strip()
    return output

REPO_PATH_STRING = get_toplevel_repo()
REPO_PATH = Path(REPO_PATH_STRING)
TESTME_PATH = REPO_PATH / ".testme"
TESTME_RUNNER_PATH = TESTME_PATH / "test_runner"
SHOULD_PRINT_STDOUT = False
SHOULD_PRINT_STDERR = False

# Assume we are calling from the root of the repo?
def get_files(commit = "HEAD"):
    """Get the file names in the commit"""
    # Command to get the name of the changed files in the latest commit
    command = f"git diff-tree --name-only -r {commit}"
    """
    Example output:

    5884411fe2853f715150a32be578da6034c015e4
    testme/tests/app_test.py
    testme/tests/sample.sh
    """
    result = run_cli("git diff-tree --name-only -r HEAD")
    output_string = result.stdout.decode("utf-8")
    files = output_string.split("\n")
    # Remove the first item, which is the commit sha
    files.pop(0)

    return files

def build_test_paths(filepaths):
    """ 
    Takes in the relative paths of the files in the git repo, and builds the Path
    objects for each
    """
    return [ Path(rel_path) for rel_path in filepaths ]

def filter_test_files(filepath):
    """Return true if the filepath contains "test" or "tests" """
    resolved_path = str(filepath.resolve())
    # We should ignore the repo path
    resolved_path = resolved_path.replace(REPO_PATH_STRING, "")
    # Get the individual parts of the path 
    components = Path(resolved_path).parts
    return "tests" in components or "test" in components

def check_for_config_folder(testme_path = TESTME_PATH):
    """Checks to see folder project_path contains the folder .testme"""
    return testme_path.exists() and testme_path.is_dir()

def check_for_test_runner(test_runner_path = TESTME_RUNNER_PATH):
    """Checks to see if the testme folder has a test runner"""
    return test_runner_path.exists() and not test_runner_path.is_dir()

def check_test_runner_executable(test_runner_path = TESTME_RUNNER_PATH):
    """Checks to see if the test runner is executable"""
    return os.access(str(test_runner_path.resolve()), os.X_OK)

def run_test(
        test_path, 
        test_runner_path = TESTME_RUNNER_PATH, 
        print_stdout = SHOULD_PRINT_STDOUT, 
        print_stderr = SHOULD_PRINT_STDERR):
    """Run the test and return True if the test passed"""
    print("🔎 " + str(test_path))
    output = run_cli(f"{test_runner_path} {str(test_path.resolve())}")
    output_string = output.stdout.decode("utf-8").strip()
    error_string = output.stderr.decode("utf-8").strip()
    return_code = output.returncode

    if output_string and print_stdout: print(green("[stdout] ") + output_string)
    if error_string and print_stderr:  print(yellow("[stderr] ") + error_string)
    
    # If the return code is not 0, then indicate something happened
    if return_code != 0:
        print(f"[ERROR] test {test_path} failed with error code {return_code}")
        return False
    
    return True

def validate_project(repo_path, testme_path):
    """Validates that our project has the necessary things in it"""
    if not check_for_config_folder():
        print(red("[ERROR] Could not find .testme folder in " + str(repo_path.resolve())).bold())
        exit(1)
    
    if not check_for_test_runner():
        print(red("[ERROR] Could not find test_runner file in " + str(testme_path.resolve())).bold())
        exit(1)

    if not check_test_runner_executable():
        print(red(f"[ERROR] Test runner {str(testme_path.resolve())} is not executable").bold())
        exit(1)
    
def run(repo_path = REPO_PATH, testme_path = TESTME_PATH, test_runner_path = TESTME_RUNNER_PATH):
    """Run the tests in the project using test runner"""
    
    # Validate that the config folder and the test runner exists
    validate_project(repo_path, testme_path)

    # Get the tests that were included in the commit
    test_paths = list(filter(
        filter_test_files, 
        build_test_paths(
            get_files())
        ))

    if not test_paths:
        return

    print(blue("Found:").italics().to_str() + "\n📄 " + "\n📄 ".join(map(str, test_paths)))
    
    tests = []

    something_failed = False

    # For each of the test files, call the test runner with the test file 
    print(blue("Executing:").italics())
    for test_path in test_paths:
        output = (test_path, True) # Second value indicates if it passed or not
        if not run_test(test_path):
            output = (test_path, False)
            something_failed = True
        tests.append(output)
    

    print(blue("Report:").italics())
    for test_path, passed in tests:
        test_path = str(test_path)
        if passed:
            print("✅ " + green(test_path))
        else:
            print("❌ " + red(test_path))


    # Return 1 if a test failed
    if something_failed:
        exit(1)


if __name__ == '__main__':
    run()
