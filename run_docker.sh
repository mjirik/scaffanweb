#!/bin/bash



docker run -d -v "/home/mjirik/projects/scaffanweb:/webapps/scaffanweb_django/scaffanweb/" -v "/home/mjirik/projects/scaffan:/webapps/scaffanweb_django/scaffan/" -p 80:8000 -p 443:443 --name scaffan scaffan:0.1
