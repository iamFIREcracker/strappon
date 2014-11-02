#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup


def get_version():
    """Gets the repository version."""
    import subprocess
    proc = subprocess.Popen('hg log -r tip --template "{latesttagdistance}"',
                            shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    pending, _ = proc.communicate()
    return "%(tag)sd%(pending)s" % dict(tag='0.0.1', pending=pending)


setup(name='strappon',
      version=get_version(),
      packages=['strappon'],
      install_requires=[
      ])
