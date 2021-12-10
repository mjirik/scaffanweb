

docker run -d -v "C:/Users/Jirik/projects/scaffanweb:/webapps/scaffanweb_django/scaffanweb/" -v "C:/Users/Jirik/projects/scaffan:/webapps/scaffanweb_django/scaffan/" -p 8000:8000 -p 8080:80 --name scaffan scaffan:0.1