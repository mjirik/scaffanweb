#!/bin/bash


sudo service redis-server start &>> logs/redis_log.txt
conda run --no-capture-output -n scaffanweb python manage.py qcluster &>> logs/qculster_log.txt
#conda run --no-capture-output -n scaffanweb python manage.py runserver 0.0.0.0:8000 &>> logs/runserver_log.txt
echo "Services started"
