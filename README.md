# Research Document Manager

In this tool users can upload the research documents and also can provide metadata about the document such as author, platform, publication date and also I am extracting content from uploaded documents and saving all these details in elasticsearch. After this user can search for keyword, so for example if user wants to search for all the research document related to “Distributed Database System” they will search it as keyword in search bar and tool will provide the best matching documents and also by clicking on individual records user will be able to read through the document as well. Also I have aggregated data based on platform, author and publication year so users can apply individual filters as well on search.

![image](https://github.com/user-attachments/assets/cda94749-d8e9-4186-8209-1412f561aabc)

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
