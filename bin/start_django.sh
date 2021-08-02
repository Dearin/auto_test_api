#!/bin/bash

NAME="auto_test"
DJANGODIR="/opt/auto_test_api"
SOCKFILE="/opt/auto_test_api/run/gunicorn.sock"
LOG="/opt/auto_test_api/log/gunicorn.log"
USER="root" # the user to run as
GROUP="root" # the group to run as
NUM_WORKERS=3 # how many worker processes should Gunicorn spawn
DJANGO_SETTINGS_MODULE="auto_test_api.settings" # which settings file should Django use
DJANGO_WSGI_MODULE="auto_test_api.asgi" # WSGI module name
IP="10.1.107.29"
TIMEOUT="300"


echo "Starting $NAME as `whoami`"

# Activate the virtual environment
cd $DJANGODIR
source ~/.virtualenvs/auto_test/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

exec  ~/.virtualenvs/auto_test/bin/daphne ${DJANGO_WSGI_MODULE}:application -b 0.0.0.0 -p 8000 --access-log $LOG&
