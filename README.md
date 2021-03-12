# testme

When working on an active pull request, often times: 

- There is only one commit, containing business logic changes and corresponding unit test changes
- I am updating the changes in the commit based on feedback from peer review 
- The updates, no matter how small, need to be validated with all the unit tests I added in the same commit 

Generally, I have the need to run all the unit tests listed in the commit. This tool does this automatically. 

## How to use

### Download
Download this repo, and add it to your path. 

### Configure
You need to have the folder `.testme` in the root of your repo. Within this folder, there should be a single executable file called `test_runner`. It should 
take in a single argument, the filepath of the test to be ran. This script should then run that single test using whatever method is done for that specifc
project. You should also add `.testme/` to your global gitignore, unless you want to commit this to the repo. 

### Running
Run the program `testme` in the root of the repo you want to test.
