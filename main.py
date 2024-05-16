## Version 0.1

from git import Repo
import os
import subprocess
from time import sleep
import requests
from urllib.error import HTTPError, URLError
import socket
import argparse
import shutil

socket.setdefaulttimeout(30)

repos = []

parser = argparse.ArgumentParser(
                    prog='GitSnap',
                    description='Archive freedom-tech git repos along with their releases',
                    epilog='')
parser.add_argument('storage_folder', help="The path where to archives should be saved to.")
parser.add_argument('-l', '--repolist', help="Text file with one git repo url per line.")
parser.add_argument('-r', '--repo', nargs='*', help="Provide a repo url via command line. Can be used multiple times.")
parser.add_argument('--prune', action='store_true', help="Prune old archives to save disk space.")
parser.add_argument('--keep-daily', help="While pruning, keep a daily backup for the last n days.")
parser.add_argument('--keep-weekly', help="While pruning, keep a weekly backup for the last n weeks.")
parser.add_argument('--keep-monthly', help="While pruning, keep a monthly backup for the last n months.")
parser.add_argument('--keep-yearly', help="While pruning, keep a yearly backup for the last n years.")
parser.add_argument('--keep-last', help="While pruning, keep the last n backups you made. Regardless of their creation dates")


args = parser.parse_args()

working_dir = args.storage_folder

# Reading repos from file
if args.repolist:
    with open(args.repolist) as file:
        for line in file:
            if not line.find("#") == 0:
                repos.append(line.rstrip())
                
if args.repo:                
    for r in args.repo:
        repos.append(r)



def clone(repourl,repopath):
    try:
        Repo.clone_from(repourl, repopath)
    except:
        print("Error cloning the repo. Skipping")
    else:
        print(f"Successfully cloned {rauthor}/{rproject}")

def update(repopath):
    try:
        repo = Repo(repopath)
        o = repo.remotes.origin
        o.pull()
    except:
        print("Error updating the repo. Skipping")


def get_asset_urls(github_link):
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.by import By
    from time import sleep
    from selenium.webdriver.firefox.options import Options


    options = Options()
    options.add_argument("-headless")

    driver = webdriver.Firefox(options=options)
    driver.get(github_link+"/releases/latest")
    sleep(2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    sleep(3)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    sleep(1)

    all_links = driver.find_elements(By.XPATH,"//a[@href]")

    links_to_download = []

    for link in all_links:
        if link.get_attribute("href").find("/releases/download/") > 1:
            links_to_download.append(link.get_attribute("href"))

    driver.quit()
    return links_to_download

def download_asset(link,path):
    from urllib.request import urlretrieve
    filename = link.split('/')[-1]
    fullpath = path+"/"+filename
    os.makedirs(os.path.dirname(fullpath), exist_ok=True)
    for tries in range(1,3):
        try:
            print(f"Downloading {filename}")
            urlretrieve(link,fullpath)
            print(f"Finished writing {filename} to disk")
        except (URLError, ConnectionError) as e:
            print("Error downloading an asset: "+str(e))
            sleep(30)
            print("Retrying in 30 seconds")
            continue
        break


def release_tag(repo):
    # Getting latest release tag
    url = repo+"/releases/latest"
    response = requests.get(url)
    if len(response.history) > 0:
        return response.url.split('/')[-1]
    else:
        print("Realease Tag ERROR")
        return "norelease"
    
def save_release_page(repo,tag,releasepath):
    releaseurl = repo+"/releases/tag/"+tag
    response = requests.get(releaseurl)
    if response.status_code == 200:
        with open(releasepath+"/RELEASE.html","wb") as file:
            file.write(response.content)
    else:
        print("No release page found.")



# Archiving one repo after the other
for repo in repos:
    r = repo.split('/')[-2:]
    rauthor = str(r[0])
    rproject = str(r[1])
    localpath = working_dir+'current/'+rauthor+'/'+rproject
    releasetag = release_tag(repo)

    print(f"Checking {rauthor}/{rproject} release {releasetag}")
    # Cloning or updating Git Repos.
    if os.path.isdir(localpath):
        print(f"Existing repo. Pulling updates (if any) for {rauthor}/{rproject}")
        update(localpath+"/repo")
    else:
        print(f"New repo. Cloning {rauthor}/{rproject} from remote.")
        clone(repo,localpath+"/repo")

# Downloading Assets

    if not os.path.isdir(localpath+"/"+releasetag):
        assets = get_asset_urls(repo)
        if assets:
            print(f"Downloading {len(assets)} latest release assets...  (tag:{releasetag})")
            for asset in assets:
                pass
                download_asset(asset,localpath+"/"+releasetag)
            # Saving Release Page as HTML
            save_release_page(repo,releasetag,localpath+"/"+releasetag)

            # Deleting old Release folder
            for folder in os.listdir(localpath):
                folderpath = localpath+"/"+folder
                if not (folderpath == localpath+"/"+releasetag or folderpath == localpath+"/repo"):
                    print(f"Deleting old release folder {folder}")
                    shutil.rmtree(folderpath)

    print("Sleeping 69 seconds to not flood")
    sleep(69)

# Checking if the borg repo exists. Create it if it does not.
if not os.path.isdir(working_dir+"archives"):
    subprocess.run(["borg","init","--encryption","none",f"{working_dir}archives"])

# Running versioned archive process
print("Creating archive...")
subprocess.run(["borg","create",f"{working_dir}archives::gitsnap-{len(repos)}repos",f"{working_dir}current"],capture_output=True)


if args.prune:
    prune_cmd = ["borg","prune"]
    if args.keep_daily:
        prune_cmd.extend(["--keep-daily",args.keep_daily])
    if args.keep_weekly:
        prune_cmd.extend(["--keep-weekly",args.keep_weekly])
    if args.keep_monthly:
        prune_cmd.extend(["--keep-monthly",args.keep_monthly])
    if args.keep_yearly:
        prune_cmd.extend(["--keep-yearly",args.keep_yearly])
    if args.keep_last:
        prune_cmd.extend(["--keep-last",args.keep_last])
    prune_cmd.append(working_dir+"archives")
    subprocess.run(prune_cmd)

print("Compacting archives to save storage space...")
subprocess.run(["borg","compact",f"{working_dir}archives"])


print("Complete!")
