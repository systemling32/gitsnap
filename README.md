# Gitsnap
#### Mirror your favorite git repositories and their releases locally in case they are taken down.

With the recent takedown of Samourai wallet's servers and their code repositories it became apparent, that all freedom-tech projects could at some point come under attack by state actors. Github will always comply with takedown requests by law enforcement and even self-hosting your repositories has not helped the Samourai team.
So if you want to make sure that the tools you use daily and are important to you, can remain public and usable, it might be smart to backup that git repo locally to some spare storage you can contribute. From there you can share your local copy with the community should the project's official repository indeed be taken down.

To make it easier to use the software after a takedown it also makes sense to save the releases as they often contain compiled binaries for quickly running that tool.

gitsnap helps you achieve this goal: simply create a text file with important repos and gitsnap will archive them locally in a provided folder.


### Features
 - Read a text file of git links that are important to you and download them including the latest releases. (Single links can also be supplied using the `-r` argument in the cli)
 - Pull any differences on locally existing repos from the remote state.
 - Works with Github, gitea and gitlab links.
 - Creates versioned archives using borg so you can roll back to earlier releases.
 - Prune old archives following specified criteria in order to save disk space.
 - Cooldown as to not exceed the 60 requests/hour limit used by GitHub for unauthenticated requests.


### Setup
*Make sure you have Python3 installed (built for 3.11) as well as pip and venv. Also you will need git and borgbackup*

Clone the code to your local machine and enter into the new directory.

`git clone https://github.com/systemling32/gitsnap && cd gitsnap`

Setup a python virtual environment, activate it and install required libraries using pip.

`python3 -m venv . && source bin/activate && pip install -r requirements.txt`


### Usage
 1. Using a list of git links (one link per line):
    
      `python3 main.py LOCAL_STORAGE_PATH -l PATH_TO_LINKLIST`
 2. Passing (several) links directly via command line arguments:
    
      `python3 main.py LOCAL_STORAGE_PATH -r LINK_TO_REPO1 -r LINK_TO_REPO2`

To prune the local archive after updating, you can additionally pass the `--prune` argument followed by either
  - `--keep-weekly n` deletes all older archive states except one state per week for the last `n` weeks.
  - Same goes for `--keep-monthly`, `--keep-yearly`
  - `--keep-last n ` prunes all but the last `n` states regardless of how long it has been between them.

Once you have your linklist and command figured out it might make sense to set the command up as a regular cronjob.

### Docker
Docker makes it all easier (of course).

`docker run --rm -d --name gitsnap -v /LOCAL/STORAGE/PATH:/storage -v /PATH/TO/LINKLIST:/repos.txt systemling32/gitsnap:latest`

Here as well you can extend that command by the prune arguments found above.

### Credits
This tool heavily relies on borg to enable versioned archives. As such it makes sense to [check out borg](https://www.borgbackup.org/) and familiarize yourself with their [usage](https://borgbackup.readthedocs.io/en/stable/usage/general.html). 
This is needed once you want to understand how to access and restore older states found in the archive/ folder or need help understanding their [prune command](https://borgbackup.readthedocs.io/en/stable/usage/prune.html).


### Contact
This is my first public code project and I know the code is shit. If you would like to contact me, you can find my profile [here](https://nostree.me/npub1qv8cgehpvylgx0euu289hm76z6czxj2qj6lqms3yt62xcw3ry39q76qq4m).
Also feel free to open issues and pull requests to improve the code and fix some of the million bugs.


## #FreeSamourai
