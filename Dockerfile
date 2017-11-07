FROM ubuntu:16.04

RUN apt-get update
RUN apt-get install -y postgresql man libpq-dev htop sudo wget python3-pip git ipython-notebook memcached htop
# Create the "developer" user
RUN useradd -c "Developer account" developer
# Make developer a sudoer
RUN echo 'developer ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers

EXPOSE 8080
# Change to the developer user and its home folder and run the entry point script
USER developer
WORKDIR /hashweb.org
