#!/bin/sh

export HOME="/home/$1"
rm -fR node_modules
npm config set cache /home/$1/.npm
npm install

export XDG_CONFIG_HOME="/home/$1/.config"
rm -fR nutrimom/static/libs/bower_components
bower cache clean
bower install --production --no-color
