import subprocess
import os
import time
from dotenv import load_dotenv
from notification import Notification

load_dotenv()

def dc_alert(payload:str) -> None:
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    if not WEBHOOK_URL:
        print("No WEBHOOK_URL set, or WEBHOOK_URL not valid. Skipping notification.")
        print(payload)
        return
    NotificationService = Notification(WEBHOOK_URL)
    NotificationService.send_notification(payload)

def main():
    dc_alert("**Starting Weekly Scrub!**🩺")
    print("Finding zpools")

    # List zpool on the system, this is piped
    p1 = subprocess.Popen(["zpool", "list"], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["awk", "{ print $1 }"], stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(["awk", "(NR>1)"], stdin=p2.stdout, stdout=subprocess.PIPE)
    out = p3.communicate()[0].decode()
    mp = [x for x in out.split("\n") if x.strip() != ""]

    # Run scrub for all zpool
    for i in mp:
        print("Running scrub for drive", i)
        # This is running in background
        subprocess.Popen(["zpool", "scrub", i])

    while True:
        status = subprocess.run(["zpool", "status"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True).stdout

        # If any of them have '% done' then its still doing scrubbing
        # Check back in an hour
        if "% done" in status:
            print("Scrub still in progress")
            time.sleep(3600)
            continue
        else:
            print("Scrub is done")

            # Split, remove drive details, then rejoin
            out = status.split("\n\n")
            new_list = []
            for (idx, i) in enumerate(out):
                if idx == 1 or (idx-1)%3 == 0:
                    continue
                new_list.extend(i.replace("\nconfig:", "").split("\n"))

            # Clean up
            new_list = [x.strip() for x in new_list if x.strip() != ""]

            # Add a new line between
            for i in range(len(new_list)-1, 0, -1):
                if (i % 4) == 0:
                    new_list.insert(i, "")

            # Bold the first line of each entry
            for idx, item in enumerate(new_list):
                if (idx % 5) == 0:
                    new_list[idx] = f"**{item}**"

            # join then split just so we reorganize the array and make sure one line have one entry
            output = f"**Weekly Scrub Report**📑\n{'\n'.join(new_list)}"
            dc_alert(output)
            break

if __name__ == "__main__":
    main()
