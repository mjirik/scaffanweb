#!/bin/bash

echo "Preparing log dir..."
mkdir -p logs

echo "Starting services..."
#sudo service redis-server start &>> logs/redis_log.txt
service redis-server start |& tee -a logs/redis_log.txt &
echo "  Redis started"
conda run --no-capture-output -n scaffanweb python manage.py qcluster |& tee -a logs/qcluster_log.txt &
conda run --no-capture-output -n scaffanweb python manage.py runserver 0.0.0.0:8000 |& tee -a logs/runserver_log.txt &
echo "Services started"

