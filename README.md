# Elasticsearch Search Tutorial

This directory contains a starter Flask project used in the Search tutorial.

## Setup steps

### Create Virtual Python Environmnet
python -m venv .venv

### Activate Virtual Environment based on OS
For Windows - .venv\Scripts\activate

### Install python libraries
pip install -r requirement.txt

### Setup Kibana and Elasticsearch in local
https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html#_linux

### Set below env variables in .env file from elasticsearch setup
  ES_HOST
  ES_USERNAME
  ES_PASSWORD
  CA_CERT_PATH
  INDEX_NAME

### Start flask application
flask run

### Create Elasticsearch Index
flask create-index --name <INDEX_NAME>

### Some helpful custom CLI commands
Create Elasticsearch Index - flask create-index --name <NAME_OF_INDEX>
Delete Elasticsearch Index - flask delete-index --name <NAME_OF_INDEX>
