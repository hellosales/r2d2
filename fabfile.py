from fabric.api import cd
from fabric.api import env
from fabric.api import local
from fabric.api import sudo

from ydcommon.fab import *
from ydcommon.fab import _check_branch
from ydcommon.fab import _get_branch_name

env.hosts = ['dev.arabel.la', ]
env.use_ssh_config = True


def _set_env():
    branch = _get_branch_name()
    user = 'r2d2-dev-api'
    prefix = "dev-api"
    environment = 'devel'
    app_dir = 'r2d2'
    if branch == 'qa' or 'release' in branch:
        user = 'r2d2-qa-api'
        prefix = "qa-api"
        environment = 'qa'
        env.hosts = 'qa.arabel.la'
    elif branch == 'master':
        env.hosts = 'r2d2.com'
        env.user = "yd"
        env.shell = "/bin/bash -c"
        prefix = "production"
        user = 'r2d2-api'
        environment = 'production'

    env.remote_user = user
    env.remote_path = '/home/%s/www/' % (user)
    env.python = '/home/%s/Envs/%s/bin/python' % (user, app_dir)
    env.pip = '/home/%s/Envs/%s/bin/pip' % (user, app_dir)
    env.prefix = prefix
    env.environment = environment
    env.app_dir = app_dir
    env.branch = branch

_set_env()


def deploy(full=False, libs=False, migrate=False, local_git=False):
    """
        Deploy new code
    """
    if local_git:
        local("git pull")
        local("git push")
    with cd(env.remote_path):
        sudo('git pull origin %s' % env.branch, user=env.remote_user)
        _check_branch(env.environment, user=env.remote_user, change=True)
        sudo('find . -name "*.pyc" -delete', user=env.remote_user)
        if full or libs:
            sudo(env.pip + ' install -r requirements.txt --no-cache-dir', user=env.remote_user)
            sudo('find /home/%s/Envs/%s/ -name "*.pyc" -delete' % (env.remote_user, env.app_dir), user=env.remote_user)
        if full or migrate:
            sudo(env.python + ' manage.py syncdb', user=env.remote_user)
            sudo(env.python + ' manage.py migrate', user=env.remote_user)
        sudo(env.python + ' manage.py collectstatic -v0 --noinput', user=env.remote_user)
        sudo(env.python + ' manage.py compress -f', user=env.remote_user)
    if env.prefix == 'production':
        sudo('supervisorctl restart r2d2-api')
        sudo('supervisorctl restart r2d2-api-celery')
    else:
        sudo('supervisorctl restart r2d2-%s' % env.prefix)
        sudo('supervisorctl restart r2d2-celery-%s' % env.prefix)
    if full:
        update_cron()
