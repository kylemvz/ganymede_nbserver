FROM jupyter/systemuser
MAINTAINER Lab41

# Update apt-get
RUN apt-get -y update

# Install gcc (required for some dependencies)
RUN apt-get -y install gcc

# Install Ganymede Logging Extension + Dependencies
COPY . /srv/ganymede_nbserver
WORKDIR /srv/ganymede_nbserver
RUN pip install -r /srv/ganymede_nbserver/requirements.txt /srv/ganymede_nbserver/.

# Execute the notebook server via bash script.
CMD ["/bin/bash", "/srv/ganymede_nbserver/ganymede_nbserver.sh"]