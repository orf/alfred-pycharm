#!/usr/bin/python
# encoding: utf-8

import sys

# Workflow3 supports Alfred 3's new features. The `Workflow` class
# is also compatible with Alfred 2.
from workflow import Workflow3
import xml.etree.ElementTree as ET
import os

LAUNCHER_DIR = '/usr/local/bin/charm'
RECENT_XPATH = ".//component[@name='RecentDirectoryProjectsManager']/option[@name='recentPaths']/list/option"


def parse_start_script(path=LAUNCHER_DIR):
    run_path, config_path = None, None
    for line in open(path, 'r'):
        line = line.strip()
        if line.startswith('CONFIG_PATH = '):
            config_path = line.split('=')[1].strip().replace("u'", '').rstrip("'")
        elif line.startswith('RUN_PATH = '):
            run_path = line.split('=')[1].strip().replace("u'", '').rstrip("'")
    return run_path, config_path


def main(wf):
    pycharm_path, config_path = parse_start_script()
    home_dir = os.path.expanduser('~')

    root = ET.parse(config_path + '/options/recentProjectDirectories.xml')
    project_paths = (
        el.attrib['value'].replace('$USER_HOME$', home_dir)
        for el in root.findall(RECENT_XPATH)
    )

    paths_with_names = (
        (path, os.path.basename(path))
        for path in project_paths
    )

    query = None
    if wf.args:
        query = wf.args[0]

    results = wf.filter(query, paths_with_names, lambda r: r[1], fold_diacritics=False)

    for path, name in results:
        wf.add_item(
            title=name,
            subtitle=path,
            uid=path,
            arg=path,
            valid=True,
            icontype='fileicon',
            icon=pycharm_path
        )

    wf.send_feedback()


if __name__ == '__main__':
    # Create a global `Workflow3` object
    wf = Workflow3()
    # Call your entry function via `Workflow3.run()` to enable its
    # helper functions, like exception catching, ARGV normalization,
    # magic arguments etc.
    sys.exit(wf.run(main))
