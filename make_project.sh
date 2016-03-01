#!/bin/bash

if [ -z "$1" ]; then
	echo "provide project name"
	exit;
fi
if [ -z "$2" ]; then
	echo "provide path to create directory for project"
	exit;
fi
if [ -z "$3" ]; then
	echo "provide project repository url"
	exit;
fi
export WORKON_HOME=~/Envs 
source /usr/share/virtualenvwrapper/virtualenvwrapper_lazy.sh
PROJECT_NAME=$1
PROJECT_PATH="$2/$PROJECT_NAME"
PROJECT_REPO=$3
TEMPLATE_PATH=`pwd`

function dbconfig {
	read -p "Database name:" dbname
	read -p "Database user:" dbuser
	read -p "Database password:" dbpass
        echo "--------------------------------------------------------------------------------------------------"
        echo "Database name: $dbname"
        echo "Database user: $dbuser"
        echo "Database password: $dbpass"
        read -p "Are you sure you wish to continue? (type: yes/no): " REPLY
	echo
	if [ "$REPLY" != "yes" ]; then
	   	dbconfig
		exit
	fi

        find $PROJECT_PATH/$PROJECT_NAME/local_settings.py -exec sed -i "s/'NAME': 'XXX',/'NAME': '$dbname',/" {} +
        find $PROJECT_PATH/$PROJECT_NAME/local_settings.py -exec sed -i "s/'USER': 'XXX',/'USER': '$dbuser',/" {} +
        find $PROJECT_PATH/$PROJECT_NAME/local_settings.py -exec sed -i "s/'PASSWORD': 'XXX',/'PASSWORD': '$dbpass',/" {} +
}

echo "--------------------------------------------------------------------------------------------------"
echo "VARIABLES:"
echo "PROJECT_NAME: $PROJECT_NAME"
echo "PROJECT_PATH: $PROJECT_PATH"
echo "PROJECT_REPO: $PROJECT_REPO"
echo "TEMPLATE_PATH: $TEMPLATE_PATH"
echo "--------------------------------------------------------------------------------------------------"

if [ -d "$PROJECT_PATH" ]; then
	echo 'Directory already exists.'
	echo 'Process terminated.'
	exit;
fi

read -p "Are you sure you wish to continue? (type: yes/no): " REPLY
echo
if [ "$REPLY" != "yes" ]; then
   exit
fi

mkvirtualenv $PROJECT_NAME --no-site-packages
workon $PROJECT_NAME
pip install django django-common

echo "--------------------------------------------------------------------------------------------------"
git clone $PROJECT_REPO $PROJECT_PATH

echo "--------------------------------------------------------------------------------------------------"
echo "Start Django Project..."
django-admin startproject $PROJECT_NAME $PROJECT_PATH -e py,conf,rst,gitignore,json --template=$TEMPLATE_PATH

echo "--------------------------------------------------------------------------------------------------"
echo "Creating local_settings.py"
cp $TEMPLATE_PATH/config/local_settings.py $PROJECT_PATH/$PROJECT_NAME/local_settings.py

echo "--------------------------------------------------------------------------------------------------"
echo "Replacing {{ project_name }} variables...";
find $PROJECT_PATH -type f -name '*' -exec sed -i "s/{{ project_name }}/$PROJECT_NAME/g" {} +

cd $PROJECT_PATH

echo "--------------------------------------------------------------------------------------------------"
echo "Initializing git flow...";
git flow init -d

echo "--------------------------------------------------------------------------------------------------"
echo "Installing requirements...";
pip install -r requirements.txt

echo "--------------------------------------------------------------------------------------------------"
echo "Initialize database settings...";
dbconfig

echo "--------------------------------------------------------------------------------------------------"
echo "Create database structure...";
./manage.py syncdb --migrate

echo "--------------------------------------------------------------------------------------------------"
echo "Cleaning up...";
rm $PROJECT_PATH/make_project.sh
deactivate $PROJECT_NAME
