#!/bin/bash

echo "Preparing log dir..."
mkdir -p logs
chmod a+rw logs

echo "Starting services..."
#sudo service redis-server start &>> logs/redis_log.txt
service redis-server start |& tee -a logs/redis_log.txt &
echo "  Redis started"
conda run --no-capture-output -n scaffanweb python manage.py qcluster |& tee -a logs/qcluster_log.txt &
# conda run --no-capture-output -n scaffanweb gunicorn scaffanweb.wsgi:application --bind 0.0.0.0:8000 --log-level=debug &
conda run --no-capture-output -n scaffanweb gunicorn scaffanweb.wsgi:application --bind 0.0.0.0:8000 --log-level=debug |& tee -a logs/runserver_gunicorn_log.txt &
# conda run --no-capture-output -n scaffanweb python manage.py runserver 0.0.0.0:8000 |& tee -a logs/runserver_log.txt &
echo "Services started"

