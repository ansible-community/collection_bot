#!/usr/bin/env python

__version__ = '1.0.0'

import os
import requests
import tempfile

from pprint import pprint

from flask import Flask
from flask import request
from flask import jsonify

from ansibullbot.utils.component_tools import AnsibleComponentMatcher
from ansibullbot.utils.git_tools import GitRepoWrapper

app = Flask(__name__)

REPO = u'https://github.com/ansible/ansible'


class BotmetaWrapper(object):
    def __init__(self, repo, cachedir='/tmp'):
        self.cachedir = cachedir
        if not os.path.isdir(self.cachedir):
            os.makedirs(self.cachedir)

        self.gitrepo = GitRepoWrapper(cachedir=self.cachedir, repo=repo)

    def render(self, botmetafile, filenames):
        component_matcher = AnsibleComponentMatcher(
            gitrepo=self.gitrepo,
            botmetafile=botmetafile,
            cachedir=self.cachedir,
            email_cache={}
        )

        results = {}
        for fn in filenames:
            results[fn] = component_matcher.get_meta_for_file(fn)
        return results

BW = BotmetaWrapper(REPO, cachedir='/tmp/botmeta')


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/render', methods=['POST'])
def render():
    data = request.get_json()
    #print(data)
    meta = data.get('current_meta')
    filepaths = data.get('filepaths')
    filepaths = filepaths.split('\n')

    pprint(filepaths)

    fh,fn = tempfile.mkstemp(dir='/tmp/botmeta', suffix='.yml')
    with open(fn, 'w') as f:
        f.write(meta)

    rendered = BW.render(
        fn,
        filepaths
    )
    pprint(rendered)

    os.remove(fn)

    return jsonify(rendered)


@app.route('/current')
def current_meta():
    url = 'https://raw.githubusercontent.com/ansible/ansible/devel/.github/BOTMETA.yml'
    rr = requests.get(url)
    return rr.text


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
