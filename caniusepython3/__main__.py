# Copyright 2014 Google Inc. All rights reserved.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
from __future__ import unicode_literals

from caniusepython3 import dependencies
from caniusepython3 import projects as projects_

import distlib.metadata
import packaging.utils

import argparse
import io
import logging
import sys

# Without this, the 'ciu' logger will emit nothing.
logging.basicConfig(format='[%(levelname)s] %(message)s')


def projects_from_cli(args):
    """Take arguments through the CLI can create a list of specified projects."""
    description = ('Determine if a set of project dependencies will work with '
                   'Python 3')
    parser = argparse.ArgumentParser(description=description)
    req_help = 'path(s) to a pip requirements file (e.g. requirements.txt)'
    parser.add_argument('--requirements', '-r', nargs='+', default=(),
                        help=req_help)
    meta_help = 'path(s) to a PEP 426 metadata file (e.g. PKG-INFO, pydist.json)'
    parser.add_argument('--metadata', '-m', nargs='+', default=(),
                        help=meta_help)
    parser.add_argument('--projects', '-p', nargs='+', default=(),
                        help='name(s) of projects to test for Python 3 support')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='verbose output (e.g. list compatibility overrides)')
    parsed = parser.parse_args(args)

    if not (parsed.requirements or parsed.metadata or parsed.projects):
        parser.error("Missing 'requirements', 'metadata', or 'projects'")

    projects = []
    if parsed.verbose:
        logging.getLogger('ciu').setLevel(logging.INFO)
    projects.extend(projects_.projects_from_requirements(parsed.requirements))
    metadata = []
    for metadata_path in parsed.metadata:
        with io.open(metadata_path) as file:
            metadata.append(file.read())
    projects.extend(projects_.projects_from_metadata(metadata))
    projects.extend(map(packaging.utils.canonicalize_name, parsed.projects))

    return projects


def message(blockers):
    """Create a sequence of key messages based on what is blocking."""
    if not blockers:
        encoding = getattr(sys.stdout, 'encoding', '')
        if encoding:
            encoding = encoding.lower()
        if encoding == 'utf-8':
            # party hat
            flair = "\U0001F389  "
        else:
            flair = ''
        return [flair +
                'You have 0 projects blocking you from using Python 3!']
    flattened_blockers = set()
    for blocker_reasons in blockers:
        for blocker in blocker_reasons:
            flattened_blockers.add(blocker)
    need = 'You need {0} project{1} to transition to Python 3.'
    formatted_need = need.format(len(flattened_blockers),
                      's' if len(flattened_blockers) != 1 else '')
    can_port = ('Of {0} {1} project{2}, {3} {4} no direct dependencies '
                'blocking {5} transition:')
    formatted_can_port = can_port.format(
            'those' if len(flattened_blockers) != 1 else 'that',
            len(flattened_blockers),
            's' if len(flattened_blockers) != 1 else '',
            len(blockers),
            'have' if len(blockers) != 1 else 'has',
            'their' if len(blockers) != 1 else 'its')
    return formatted_need, formatted_can_port


def pprint_blockers(blockers):
    """Pretty print blockers into a sequence of strings.

    Results will be sorted by top-level project name. This means that if a
    project is blocking another project then the dependent project will be
    what is used in the sorting, not the project at the bottom of the
    dependency graph.

    """
    pprinted = []
    for blocker in sorted(blockers, key=lambda x: tuple(reversed(x))):
        buf = [blocker[0]]
        if len(blocker) > 1:
            buf.append(' (which is blocking ')
            buf.append(', which is blocking '.join(blocker[1:]))
            buf.append(')')
        pprinted.append(''.join(buf))
    return pprinted


def check(projects):
    """Check the specified projects for Python 3 compatibility."""
    log = logging.getLogger('ciu')
    log.info('{0} top-level projects to check'.format(len(projects)))
    print('Finding and checking dependencies ...')
    blockers = dependencies.blockers(projects)

    print('')
    for line in message(blockers):
        print(line)

    print('')
    for line in pprint_blockers(blockers):
        print(' ', line)

    return len(blockers) == 0


def main(args=sys.argv[1:]):
    passed = check(projects_from_cli(args))
    if not passed:
      sys.exit(3)


if __name__ == '__main__':  #pragma: no cover
    main()
