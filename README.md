# remarkable-todo

I write my to-do list by hand on a reMarkable tablet. I like writing tasks down as they come up instead of typing them, but then I get no reminders, the list isn't on my phone or laptop, and nothing goes on my calendar.

So this reads the page when I put the pen back in its dock, and:
- new tasks go to Todoist and get the next free half hour on my Google Calendar today
- if I tick a task or cross it out on paper it gets completed in Todoist

![check.py output](images/example.png)

## How it works

1. `tablet/pen_dock.sh` runs on the tablet and waits for the pen to go back in the dock. Then it copies the page to my Mac and runs `sync.py` there over ssh.
2. `sync.py` reads the page file with [rmscene](https://github.com/ricklupton/rmscene), which gives every pen stroke as a list of x, y points.
3. I use the Checklist template that comes with the tablet, so every task is on a row with a box. Each stroke goes in the row where its middle is, and a stroke inside the box is a tick. A stroke wider than 300 pixels counts as a line through the task. Either one means done.
4. The rest of the row is cropped out of a picture of the page and read with Apple's Vision framework. It runs on the Mac, no API key needed.
5. The rows are compared with `last_sync.json` (what the page looked like last time) so only new rows become tasks.

`utils.py` has the functions for reading the page. `check.py` draws the template rows on top of a page, I used it a lot for debuging.

## Try it

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python check.py test_pages/after.rm
```

`test_pages/before.rm` is a page I wrote, `after.rm` is the same page after ticking one task, crossing one out and adding two more.

## Setup

Mac only (Vision is part of macOS).

**Todoist:** put your API token (Settings > Integrations > Developer) in `todoist_token.txt`.

**Google Calendar:** follow Google's Python quickstart for the Calendar API to make a project and download `credentials.json` into this folder. Then run `python sync.py test_pages/before.rm` once on the Mac, it opens the browser to log in and saves `token.json`. After that it works without the browser. Publish the app in the Google Cloud console (it can stay unverified), apps in "testing" mode have to log in again every 7 days.

Careful, running sync.py on a test page creates real tasks and calendar events.

**Mac:** turn on Remote Login (System Settings > General > Sharing). Keep the project in your home folder (`~/remarkable-todo`), not in Documents or Desktop, ssh can't open files there. Make an empty `pages` folder in it, that's where the tablet copies the page.

**Tablet:** you need developer mode to get ssh into the tablet.
1. On the tablet make a key with `dropbearkey -t ed25519 -f ~/.ssh/id_dropbear` and add the public key it prints to `~/.ssh/authorized_keys` on the Mac.
2. In `tablet/pen_dock.sh` put your Mac's user and IP address, the notebook id and the page id (the folder and file names under `/home/root/.local/share/remarkable/xochitl/`).
3. Copy it to the tablet and start it with `nohup sh pen_dock.sh &`
