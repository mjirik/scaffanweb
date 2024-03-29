# FROM nginx
FROM continuumio/miniconda3
# FROM jammy
MAINTAINER Miroslav Jiřík <mjirik@kky.zcu.cz>
EXPOSE 8000
# RUN useradd -ms /bin/bash scaffanweb
# USER scaffanweb

WORKDIR /webapps
#VOLUME .. /
SHELL ["/bin/bash", "--login", "-c"]
RUN apt-get update --yes
# PyQt5 => ffmpeg libsm6 libxext6
RUN apt-get install --yes gpg vim redis ffmpeg libsm6 libxext6 curl
# Install our public GPG key to trusted store
RUN curl https://repo.anaconda.com/pkgs/misc/gpgkeys/anaconda.asc | gpg --dearmor > conda.gpg
RUN install -o root -g root -m 644 conda.gpg /usr/share/keyrings/conda-archive-keyring.gpg

# Check whether fingerprint is correct (will output an error message otherwise)
RUN gpg --keyring /usr/share/keyrings/conda-archive-keyring.gpg --no-default-keyring --fingerprint 34161F5BF5EB1D4BFBBB8F0A8AEB4F8B29D82806

# Add our Debian repo
RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/conda-archive-keyring.gpg] https://repo.anaconda.com/pkgs/misc/debrepo/conda stable main" > /etc/apt/sources.list.d/conda.list
RUN apt-get update --yes
RUN apt-get install --yes conda

# make conda visible
RUN echo "source /opt/conda/etc/profile.d/conda.sh" >> /root/.bashrc
RUN /opt/conda/condabin/conda init bash
# SHELL ["/bin/bash", "--login", "-c"]
# RUN source /opt/conda/etc/profile.d/conda.sh

# fix missing libffi.6 on some version of ubuntu
RUN curl -L http://mirrors.kernel.org/ubuntu/pool/main/libf/libffi/libffi6_3.2.1-8_amd64.deb -o libffi6.deb
RUN apt-get install ./libffi6.deb


# SHELL ["/bin/bash", "--login", "-c"]
# RUN ls

# this is done before the final conda installation to make the docker re-build faster
RUN /opt/conda/condabin/conda create -n scaffanweb -c mjirik -c bioconda -c simpleitk -c conda-forge --yes openslide-python "python>=3.6.2,=3.6" pip pytest pytest-cov tensorflow=2.2 loguru redis-py redis
# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "scaffanweb", "/bin/bash", "-c"]

# the next line is probably not necessary and causing the rebuild of docker on every change
# COPY scaffanweb .
COPY requirements_conda_pinned.txt .

RUN /opt/conda/condabin/conda install -n scaffanweb -c mjirik -c bioconda -c simpleitk -c conda-forge --yes --file requirements_conda_pinned.txt openslide-python pip pytest pytest-cov tensorflow=2.2 loguru redis-py redis scaffan>=0.32
RUN /opt/conda/condabin/conda install -n scaffanweb -c conda-forge --yes pcre
#RUN cd /webapps/scaffanweb_django
# Make RUN commands use the new environment:
# SHELL ["conda", "run", "-n", "scaffanweb", "/bin/bash", "--login", "-c"]
# RUN /opt/conda/condabin/conda init bash
COPY requirements_pip.txt .
RUN /opt/conda/condabin/conda run -n scaffanweb --no-capture-output pip install -r requirements_pip.txt

RUN /opt/conda/condabin/conda list -n scaffanweb

COPY deploy/var /var/
COPY deploy/etc /etc/
ENV TZ="Europe/Berlin"


WORKDIR /webapps/scaffanweb_django/scaffanweb

RUN mkdir -p /webapps/scaffanweb_django/static

# Make RUN commands use the new environment:
# SHELL ["conda", "run", "-n", "scaffanweb", "/bin/bash", "-c"]

CMD cd /webapps/scaffanweb_django/scaffanweb && \
    bash /webapps/scaffanweb_django/scaffanweb/run_services.sh && \
    tail -f /dev/null

#    /webapps/piglegsurgery/docker/bin/qcluster_start  & && \
#    /webapps/piglegsurgery/docker/bin/gunicorn_start & && \
#    service redis-server start && \
# CMD ["cd", "/webapps/scaffanweb_django"]
# ENTRYPOINT ["python", "manage.py", 'runserver']
