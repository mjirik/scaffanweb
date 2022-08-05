  
[![Build Status](https://travis-ci.org/mjirik/scaffanweb.svg?branch=master)](https://travis-ci.org/mjirik/scaffanweb)
[![Coverage Status](https://coveralls.io/repos/github/mjirik/scaffanweb/badge.svg?branch=master)](https://coveralls.io/github/mjirik/scaffanweb?branch=master)
[![PyPI version](https://badge.fury.io/py/scaffanweb.svg)](http://badge.fury.io/py/scaffanweb)


scaffanweb

Web application for scaffold analysis from H&E stained images


# Install with docker

```bash

cd scaffanweb
docker build -t scaffan:0.1 .
```

```bash
docker run -d -v "C:/Users/Jirik/projects/scaffanweb:/webapps/scaffanweb_django/scaffanweb/" -v "C:/Users/Jirik/projects/scaffan:/webapps/scaffanweb_django/scaffan/" -p 8000:8000 -p 8080:80 --name scaffan scaffan:0.1
```
