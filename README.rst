.. image:: https://requires.io/bitbucket/arabellatech/django-project-template/requirements.svg?branch=master
     :target: https://requires.io/bitbucket/arabellatech/django-project-template/requirements/?branch=master
     :alt: Requirements Status

********
R2d2
********

.. contents::

Prerequisites
=============
Python > 2.6, PIP, Homebrew (Mac OSX), Git (and a github account), VirtualEnv (mkvirtualenv helper script), gitflow

Dev requirements
================
**MySQL, Nginx**


*Ubuntu*

::

    sudo apt-get install git python-dev python-pip libxml2-dev libxslt1-dev libmysqlclient-dev, libjpeg-dev


Getting Started
===============
Preparing virtualenv paths (optional if your profile doesn't have it).

::

    export WORKON_HOME=~/Envs
    source /usr/bin/virtualenvwrapper_lazy.sh
    # or
    source /usr/local/bin/virtualenvwrapper_lazy.sh

Start by creating a virtual environment using the helper scripts provided. Do not include the systems site-packages.

::

    mkvirtualenv r2d2 --no-site-packages
    workon r2d2

Clone the Github repository if you have not done so yet. You will need a git account to do this.

::

    git clone git@bitbucket.com:ArabellaTech/r2d2.git

Move into the newly created Project Data folder.

Initialize GitFlow (More info: http://wiki.ydtech.co/developers:gitflow)

::

    git flow init -d

Install the Python requirements using PIP, which are located in the requirements.txt file. Ensure the platform requirements are installed (python-dev/python-devel).

::

    pip install -r requirements.txt

Create local settings or copy one from config/develop into your project root and custom it.

::

    cp config/local_settings.py r2d2/local_settings.py

Upon successful completion of the installation initialize the database. (NOTE: database must be running.)

::

    ./manage.py migrate


**Get Sass and bower**

update ruby if your version is low - check:

::

    ruby -v

Compare with version on https://www.ruby-lang.org/en/downloads/
If your version is OLD update it with:

::

    curl -L https://get.rvm.io | bash -s stable --ruby


Make sure sass is at least in 3.3.0 version to use advanced debuging in chrome.

::

    gem install compass -v 1.0.0.alpha.19
    gem install sass -v 3.4.0

Be sure to have

::

    INTERNAL_IPS = (
        "127.0.0.1",
        "all others IPS used for development",
    )

in your local settings, otherwise live reload of css will not work.

Hint: if you use FireFox for development try this:
https://addons.mozilla.org/en-US/firefox/addon/firesass-for-firebug/

Create the static

::

    ./manage.py bower_install
    ./manage.py collectstatic -v0 --noinput
    ./manage.py compress -f

If this is the first time through, create the superuser account

::

    ./manage.py createsuperuser


Launching
=========

Use gulp to update watch for changes in sass files and generate them on the fly

::

    gulp

Alternatively you can use python sass

::

    python sass.py

Start the server

::

./manage.py runserver