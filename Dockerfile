FROM jupyter/systemuser
MAINTAINER Lab41

# Update apt-get
RUN apt-get -y update

# Install gcc (required for some dependencies)
RUN apt-get -y install gcc

# Install Ganymede Logging Extension + Dependencies
COPY . /ganymede_nbserver
RUN pip install -r /ganymede_nbserver/requirements.txt /ganymede_nbserver/. && \
    rm -rf /ganymede_nbserver