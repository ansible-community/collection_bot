#!/usr/bin/env python3
import os
import sys
import yaml
from github import Github, GithubException

if os.environ.get('GITHUB_PUBLIC_REPO_TOKEN'):
    g = Github(os.environ.get('GITHUB_PUBLIC_REPO_TOKEN'))
else:
    print("Token not defined, needs public:repo from https://github.com/settings/tokens")
    sys.exit(1)


"""
labels.yml should contain the names, hex color, and descriptions (if wanted) for your labels:
```yaml
----
- name: needs_triage
  color: ededed
  description: None
- color: 0e8a16
  name: pr_day
  description: 'Has been reviewed during a PR review Day. https://github.com/ansible/community/issues/407'
```

You can create this file from an existing repo like:
```python
source_repo = g.get_repo("ansible-collections/community.general")
labels = source_repo.get_labels()
label_dict = [{ 'name': i.name, 'color': i.color, 'description': i.description } for i in labels ]
with open('labels.yml', 'w') as f:
    yaml.dump(label_dict, f, width=1000)
```
"""

REPOS = [
        'ansible-collections/community.general',
        'ansible-collections/community.network',
#       'ansible-collections/community.'.
#       'ansible-collections/community.general'.
#       'ansible-collections/community.general'.

        ]
with open('labels.yml', 'rb') as f:
    want_labels = yaml.safe_load(f)

for repo_name in REPOS:
    print(repo_name, end=' ', flush=True)
    repo = g.get_repo(repo_name)

    # label_response = dest_repo.get_labels()
    # current_labels = [{ 'name': i.name, 'color': i.color, 'description': i.description } for i in label_response]
    # we could do something with comparing the current and desired labels here

    for label in want_labels:
        print(".", end = '', flush=True)
        if label['description'] is not None:
            create_args = dict(name=label['name'], color=label['color'], description=label['description'])
        else:
            create_args = dict(name=label['name'], color=label['color'])

        try:
            repo.create_label(**create_args)
        except GithubException as e:
            if e.data['errors'][0]['code'] == 'already_exists':
                repo.get_label(label['name']).edit(**create_args)
    print("")
