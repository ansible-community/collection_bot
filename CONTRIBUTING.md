# Collection Bot Contributor's Guide

## Python compatibility

Collection Bot is compatible with Python 3.8+.

## Getting started

1. Fork this repo.
2. Clone your fork.
3. Create a feature branch.
4. Optionally: create a [Python virtual environment](https://realpython.com/python-virtual-environments-a-primer/) and activate it.
4. Install the python requirements: `pip install -r requirements.txt`.
5. Create the default log file `/var/log/ansibullbot.log` with appropriate permissions or use the `--log=<PATH>` argument to specify a custom log file when running your tests. For the default file, the command might look like:
    * `sudo touch /var/log/ansibullbot.log && sudo chmod 777 /var/log/ansibullbot.log`
6. Create the config file, copy [`examples/ansibullbot.cfg`](https://github.com/ansible-community/collection_bot/blob/main/examples/ansibullbot.cfg) to one of these paths:
    * `~/.ansibullbot.cfg`
    * `$CWD/ansibullbot.cfg`
    * `/etc/ansibullbot/ansibullbot.cfg`
    * define `ANSIBULLBOT_CONFIG` environment variable where the configuration file is located.
7. Fill in the credentials.
8. Optionally: create a cache directory, for example, with `mkdir /tmp/cache`. Adjust permissions if needed.

## Testing your changes

**IMPORTANT:** If you do NOT want the bot to make any changes in issues/PRs, remember to use the `--dry-run` argument!

The basic command to run the bot in testing mode is:

```bash
./triage_ansible.py --debug --verbose --dry-run
```

Also consider using the `--id <ISSUE/PR-NUMBER` argument if you have a specific issue to test against. It can speed up testing dramatically.

Other useful arguments might be:
- `--logfile <PATH>`: path to an arbitrary logfile.
- `--cachedir <PATH>`: cache in a specified existing directory.
- `--resume`: pickup right after where the bot last stopped.
- `--force`: do not ask questions.
- `--ignore_galaxy`: do not index or search for components in galaxy.
- `--dump_actions`: serialize the actions to disk.
- `--botmetafile`: path to BOTMETA.yml. see the section below for details.

So the command might be:

```bash
./triage_ansible.py --debug --dry-run --id=<NUM> --resume --force --ignore_galaxy --dump_actions --logfile=/tmp/ansibullbot.log --cachedir=/tmp/cache --botmetafile=/tmp/BOTMETA.yml
```

## Testing changes to BOTMETA.yml

1. Download the `.github/BOTMETA.yml` file from a target repository to a local directory.
2. Edit the file with whatever changes you want to make.
3. Run your testing command with the `--botmetafile=<PATHTOFILE>` argument.

## Testing changes related to a single label

**TBD: Needs to be checked if this info is still relevant**

The `--id` parameter can take a path to a script. The `scripts` directory is full of scripts that will return json'ified lists of issue numbers. One example is the `scripts/list_open_issues_with_needs_info.sh` script which scrapes the github UI for any issues with the needs_info label. Here's how you might use that to test your changes to ansibullbot against all issues with needs_info ...

```
./triage_ansible.py --debug --verbose --dry-run --id=scripts/list_open_issues_with_needs_info.sh
```

## Running the bot as a service

**IMPORTANT:** This wasn't tested. It was derived from the current server configuration using common sense and normal possible course of events to make it up and running. If you're deploying a new instance, please improve this document along the way.

1. Set up things and run the bot in testing mode as described in the previous sections.
2. Create the `/var/lib/ansibot` directory.
3. Move/copy the bot's repo you used for testing to `/var/lib/ansibot/ansibullbot`.
4. If you succeeded, create a non-privileged user to run the bot as a service.
5. Put the config file to `/var/lib/ansibot/.ansibullbot.cfg`.
6. Make the user an owner of `/var/lib/ansibot` recursively.
7. Make sure the user has permissions to write to the log file specified in unit files below.
8. Run the bot in testing mode from that directory again.
9. Create systemd units for `ansibullbot` and `ansibullbot-receiver`. Samples of unit files:

```bash
# cat /etc/systemd/system/ansibullbot.service

# Ansible managed
[Unit]
Description=Ansibullbot
After=syslog.target

[Service]
Type=simple
User=ansibot
Group=ansibot

Restart=on-failure

StandardOutput=null
StandardError=null

Environment="PATH=/var/lib/ansibot/venv/bin:/sbin:/bin:/usr/sbin:/usr/bin"
ExecStart=/var/lib/ansibot/venv/bin/python /var/lib/ansibot/ansibullbot/triage_ansible.py --daemonize --daemonize_interval=300 --debug --force --logfile /var/log/ansibullbot.log --resume --ignore_galaxy --skip_no_update --dump_actions

WorkingDirectory=/var/lib/ansibot/ansibullbot

[Install]
WantedBy=multi-user.target
```

```bash
# cat /etc/systemd/system/ansibullbot-receiver.service

# Ansible managed
[Unit]
Description=Ansibullbot Receiver
After=syslog.target

[Service]
Type=simple
User=ansibot
Group=ansibot

Restart=on-failure

ExecStart=/var/lib/ansibot/venv/bin/python /var/lib/ansibot/ansibullbot/scripts/ansibot_receiver.py
WorkingDirectory=/var/lib/ansibot/ansibullbot

[Install]
WantedBy=multi-user.target
```
10. Run the units via `systemctl`.


## Updating Ansible Playbooks and Roles used by Ansibullbot ##

**TBD: Needs to be checked if this info is still relevant**

Ansibullbot is deployed and managed using [Ansible](https://www.ansible.com) and [Ansible Tower](https://www.ansible.com/tower). There are several roles used by Ansibullbot, each of which is a [git submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules).

When making changes anything besides the roles, make the changes to this repository and submit a pull request.

When making changes to roles, first submit pull request to the role repository and ensure it is merged to the pull request repository. Then, submit a pull request to this repository updating the submodule to the include the new commit.

To update the role submodule and include it in your pull request:

1. Run `git submodule update --remote [path to role]` to pull in the latest role commits.
1. `git add [path to role]`
1. Commit and push the branch to your fork
2. Submit the pull request
