from cookiecutter.main import cookiecutter
import os
import psutil
import pkg_resources


def process(args):
    # Create project from the cookiecutter-pypackage/ template
    extra_context = {
        'publish_host': os.uname()[1],
        'docker_host_cache_dir': os.path.join(os.getcwd(), 'cache',),
        'docker_host_publish_dir': os.path.join(os.getcwd(), 'publish'),
        'cache_dir': os.path.join(os.getcwd(), 'cache',),
        'publish_dir': os.path.join(os.getcwd(), 'publish'),
        'twice_no_of_cores': psutil.cpu_count() * 2,
    }
    template = args.source + '-docker' if args.container else args.source
    template_dir = os.path.join(
        pkg_resources.resource_filename('ronto', 'data/'), template)
    cookiecutter(template_dir, extra_context=extra_context)


def add_command(subparser):
    parser = subparser.add_parser(
        "bootstrap",
        help="""
        Create a new Yocto build project from scratch. You will
        be asked a couple of questions and end up with a ronto.yml
        file and an optional site.conf file
        """,
    )
    parser.add_argument('-s', '--source', choices=[ 'repo', 'git', 'ignore' ],
        default='git',
        help="""
        Select how build configuration sources are maintained:
        repo - via google repo tool
        git - by a set of git repositories
        ignore - ronto does not take care for sources

        Default is git
        """)
    parser.add_argument('-c', '--container', action='store_true',
        help="Run in docker container")
    parser.set_defaults(func=process)
