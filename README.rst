.. image:: https://requires.io/bitbucket/arabellatech/r2d2/requirements.svg?branch=develop
     :target: https://requires.io/bitbucket/arabellatech/r2d2/requirements/?branch=develop
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

:: install mongo

    brew install mongodb

:: run mongo

    mongod --dbpath "SOME_PATH_TO_DATA" --directoryperdb &

mongo by default runs on port 27017, you can override it with --port option

Add mongo settings to your local_settings:

    MONGODB_DATABASES = {
        'mongo': {
            'name': 'r2d2',
            'username': '',
            'password': '',
            'host': 'localhost',
            'port': 27017,
        }
    }

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


Money exchange rates
====================

To download exchange rates daily add to cron:

::
    manage.py update_rates yesterday

Please note that we are using average rates, that is why we don't pull data for current day, always for the day before.

To fill up rates history run:

::
    manage.py update_rates date_from[YYYY-MM-DD] date_to[YYYY-MM-DD]

Please mind the 1000 calls/month limit while filling up history! (1 day = 1 call)


Etsy/Shopify/Squareup
=====================

Configure Site with your server domain (/admin/sites/site/).
Please note: squareup default settings works only with localhost:8000.

Go to admin:

    http://localhost:8000/admin/etsy_api/etsyaccount/
    http://localhost:8000/admin/shopify_api/shopifystore/
    http://localhost:8000/admin/squareup_api/squareupaccount/

and create an account for the service you want. For Etsy/Squareup name is just our identifier and may be chosen at will,
however for Shopify it must point to existing store. Our test store is: arabel-la-store

Run shell and get authorization urls:

::
    ./manage.py shell

    from r2d2.shopify_api.models import ShopifyStore
    from r2d2.etsy_api.models import EtsyAccount
    from r2d2.squareup_api.models import SquareupAccount

    ShopifyStore.objects.all()[0].authorization_url
    EtsyAccount.objects.all()[0].authorization_url
    SquareupAccount.objects.all()[0].authorization_url


Paste the links generated above to the browser (you must be logged in as the user that created above accounts),
you should get 200 OK response. Once done, you may access to the access_token in the admin pages linked above.
Logins for each services can be found in the following document

::

    https://docs.google.com/document/d/1uI3EgX72Zc45UzxV6sFFznyLISpcbE5rVfzjR0_ZqJw/edit


If you get empty string instead of authorization_url it probably means you've already authorized the account - check in
admin if you have access token for it.

