import os
import sys
import shutil

def remove_file(file):
    """ Remove file path is local from working dir """
    try:
        os.remove(file)
    except Exception:
        pass


def before_tag(context, tag):
    if tag.startswith('before.clean') or tag.startswith('clean'):
        remove_file('site.conf')
        shutil.rmtree('build', ignore_errors=True)
        shutil.rmtree('sources', ignore_errors=True)

def after_tag(context, tag):
    if tag.startswith('after.clean') or tag.startswith('clean'):
        remove_file('site.conf')
        shutil.rmtree('build', ignore_errors=True)
        shutil.rmtree('sources', ignore_errors=True)
