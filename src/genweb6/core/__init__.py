# -*- coding: utf-8 -*-
from zope.i18nmessageid import MessageFactory

import os
import pkg_resources
import subprocess
import sys

try:
    pkg_resources.get_distribution('upcnet.cas')
except pkg_resources.DistributionNotFound:
    HAS_CAS = False
else:
    HAS_CAS = True

try:
    pkg_resources.get_distribution('plone.app.contenttypes')
except pkg_resources.DistributionNotFound:
    HAS_DXCT = False
else:
    HAS_DXCT = True

try:
    pkg_resources.get_distribution('plone.app.multilingual')
except pkg_resources.DistributionNotFound:
    HAS_PAM = False
else:
    HAS_PAM = True

_ = GenwebMessageFactory = MessageFactory('genweb')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""


def install_pre_commit_hook(argv=sys.argv):
    if len(argv) != 2:
        cmd = os.path.basename(argv[0])
        print('usage: %s <sources_path>\n'
              '(example: "%s /Development/ulearn.buildout/src")' % (cmd, cmd))
        sys.exit(1)

    sources_path = argv[1]
    repos = os.listdir(sources_path)

    for repo in repos:
        git_hooks_directory = sources_path + '/' + repo + '/.git/hooks'

        if not os.path.exists(git_hooks_directory):
            print('Unable to create git pre-commit hook, '
                  'this does not seem to be a git repository.')
            return

        with open(git_hooks_directory + '/pre-commit', 'w') as output_file:
            output_file.write(
                '#!/bin/bash\n{}/bin/code-analysis-{}'.format(sources_path.replace('/src', ''), repo))

        subprocess.call([
            'chmod',
            '775',
            git_hooks_directory + '/pre-commit',
        ])

        print('Install Git pre-commit hook in {}.'.format(repo))


def uninstall_pre_commit_hook(argv=sys.argv):
    if len(argv) != 2:
        cmd = os.path.basename(argv[0])
        print('usage: %s <sources_path>\n'
              '(example: "%s /Development/ulearn.buildout/src")' % (cmd, cmd))
        sys.exit(1)

    sources_path = argv[1]
    repos = os.listdir(sources_path)

    for repo in repos:
        git_hooks_directory = repo + '/.git/hooks'

        try:
            os.remove(git_hooks_directory + '/pre-commit')
        except OSError:
            pass

        print('Uninstall Git pre-commit hook in {}.'.format(repo))
