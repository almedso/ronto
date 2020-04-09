import os
import re
from setuptools import setup, find_packages

regexp = re.compile(r'.*__version__ = [\'\"](.*?)[\'\"]', re.S)

base_package = 'ronto'
base_path = os.path.dirname(__file__)

init_file = os.path.join(base_path, 'src', 'ronto', '__init__.py')
with open(init_file, 'r') as f:
    module_content = f.read()

    match = regexp.match(module_content)
    if match:
        version = match.group(1)
    else:
        raise RuntimeError(
            'Cannot find __version__ in {}'.format(init_file))

with open('README.rst', 'r') as f:
    readme = f.read()

with open('CHANGELOG.rst', 'r') as f:
    changes = f.read()

def parse_requirements(filename):
    ''' Load requirements from a pip requirements file '''
    with open(filename, 'r') as fd:
        lines = []
        for line in fd:
            line.strip()
            if line and not line.startswith("#"):
                lines.append(line)
    return lines

requirements = parse_requirements('requirements.txt')


if __name__ == '__main__':
    setup(
        name='ronto',
        description=' Wrapper around building stuff using repotool and Yocto',
        long_description='\n\n'.join([readme, changes]),
        license='MIT license',
        url='https://github.com/almedso/ronto',
        version=version,
        author='Volker Kempert',
        author_email='volker.kempert@almedso.de',
        maintainer='Volker Kempert',
        maintainer_email='volker.kempert@almedso.de',
        install_requires=requirements,
        keywords=['ronto'],
        package_dir={'': 'src'},
        packages=find_packages('src'),
        zip_safe=False,
        entry_points={
            "console_scripts": [
                "ronto = main:main",
            ]
        },
        classifiers=['Development Status :: 3 - Alpha',
                     'Intended Audience :: Developers',
                     'Intended Audience :: Information Technology',
                     'Topic :: Software Development :: Build Tools',
                     'Topic :: Utilities',
                     'Environment :: Console',
                     'Programming Language :: Python :: 3.6'],
        project_urls={
            'Documentation': 'https://ronto.readthedocs.io',
            'Bug Reports': 'https://github.com/almedso/ronto/issues',
            'Source': 'https://github.com/almedso/ronto/',
    }
    )
