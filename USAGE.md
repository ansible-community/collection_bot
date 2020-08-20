Running Ansibullbot
===================

How to deploy and run ansibullbot for one or more collections.

Requirements
------------

* AWS account
* Github account
* Python2.7 environment

Setup
-----

* Clone this repo (with the correct branch) to your local machine.
* Sync the submodules
```shell script
collection_bot$ git submodule init
collection_bot$ git submodule update
```
* Setup AWS authentication using either a
[boto profile](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html)
or environment variables. See the
[Ansible AWS Guide](https://docs.ansible.com/ansible/devel/scenario_guides/guide_aws.html#authentication)
for more details.
* Copy `examples/ansibullbot.cfg` to the root of the repository.
* Fill in the `repo` value(s) of the repositories your bot is permitted to be run against.
* Edit `ansibullbot/triagers/ansible.py` to update the `repo_data` dictionary with your branch information
and, if applicable, Shippable project details.


Running ansibullbot
-------------------

Ansibullbot can be run ad-hoc on the command line or as a daemon.  It is recommended to run the bot in a virtual 
environment for ad-hoc use.  The below assumes you have setup your `ansibullbot.cfg` as described in the previous
section, and made the necessary edits to `ansibullbot/triagers/ansible.py`.  Any repositories passed with `--repo`
must be enabled in your ansibullbot.cfg file.

```shell script
$ cd collection_bot/
$ python2.7 -m virtualenv .ansibot
$ source .ansibot/bin/activate
$ python2.7 -m pip install -r requirements.txt
$ python2.7 -m pip install epdb  ## Ansibullbot has breakpoints, epbd must be installed if one it hit
$ python2.7 triage_ansible.py --repo ansible-collections/mycollection --repo ansible-collections/some_other_repo
```

See `python2.7 triage_ansible.py --help` for more options, including daemonize, dry-run, and debug flags.

Deploying to AWS
----------------

This repo ships with playbooks that, along with the references submodules, will deploy the bot to an AWS EC2 instance
where it can be run as a daemon along with a public status webpage and reports. This step is optional, the bot can be run
from any host the operator prefers.

The roles and playbooks used for deploying and managing the bot instance contain a number of variables and values
that will need to be customized for your deployment.  You will want to create an `inventory.yml` file with the
following vars, customized as needed (this method assumes example.com uses Route53 for DNS).

Be sure that the ssh key for the user you are currently running as is the first entry in the botinstance_ssh_keys
dictionary.  This is the key that will be provided to ec2_instance and used for bot installation tasks.

```yaml
all:
  vars:
    botinstance_name: ansibullbot-mycollection
    botinstance_region: us-west-1
    botinstance_volume_size: 200
    botinstance_type: t3.xlarge
    botinstance_ssh_keys:
      - name: mykey
        key_material: ssh-rsa 12345567890aaaaaaaaaaaa...
    ansibullbot_fqdn: ansibullbot-mycollection.example.com
    botinstance_dns_entries:
      - type: CNAME
        record: ansibot-mycollection.example.com
        value: ansibullbot-mycollection.example.com
    
      - type: CNAME
        record: ansiblebot-mycollection.example.com
        value: ansibullbot-mycollection.example.com
    
      - type: A
        command: create
        record: ansibullbot-cloud.enxample.com
        value: "{{ _elastic_ip.public_ip }}"

    ansibullbot_repos:  ## List
      - ansible-collections/mycollection
      - ansible-collections/some_other_repo

    ansibullbot_options:
      - daemonize
      - daemonize_interval={{ ansibullbot_daemonize_interval }}
      - debug
      - force
      - logfile {{ ansibullbot_log_path }}
      - resume
      - skip_no_update
      - skip_no_update_timeout
      - verbose
      {% for collection in ansibullbot_repos %}
      - repo "{{ repo }}"
      {% endfor %}
    
    ansibullbot_github_username: yourbotname
    ansibullbot_repo_url: https://github.com/ansible-collections/collection_bot
    ansibullbot_branch: main
    
    ansibullbot_github_token: xxxxxxxxxxxxxxxxxxxxxx
    
    ansibullbot_shippable_token: xxxxxxxxxxxxxxxxxxxxxx
    
    ### Optional if you want ansibullbot to send slack notifications
    ansibullbot_slack_url: ''
    
    ### Optional if you want ansibullbot to send slack notifications
    ansibullbot_slack_token: ''
    
    ### Optional if you want ansibullbot to send email notifications
    ansibullbot_notify_email: ''
    
    ### Optional if you want ansibullbot to send sentry notifications
    ansibullbot_sentry_url: ''

```

```shell script
pip install boto3 botocore
ansible-playbook -i inventory.yml setup-ansibullbot.yml
```
