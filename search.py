import json
from pprint import pprint
from dotenv import load_dotenv
from elasticsearch import Elasticsearch, NotFoundError
import os

load_dotenv()

ES_HOST = os.environ['ES_HOST']
ES_USERNAME = os.environ['ES_USERNAME']
ES_PASSWORD = os.environ['ES_PASSWORD']
CA_CERT_PATH = os.environ['CA_CERT_PATH']
INDEX_NAME = os.environ['INDEX_NAME']

class Search:
    def __init__(self, mapping={}, index_name=INDEX_NAME):
        # self.es = Elasticsearch(cloud_id=os.environ['ELASTIC_CLOUD_ID'], api_key=os.environ['ELASTIC_API_KEY'])
        self.es = Elasticsearch(ES_HOST, basic_auth=(ES_USERNAME, ES_PASSWORD), ca_certs=CA_CERT_PATH)
        self.index_name = index_name
        self.mapping = mapping
        client_info = self.es.info()
        print('Connected to Elasticsearch!')
        pprint(client_info.body)

    def create_index(self, name = ''):
        if not name:
            name = self.index_name
        self.index_name = name
        self.delete_index(name)
        self.es.indices.create(index=name, body=self.mapping)

    def delete_index(self, name):
        self.es.indices.delete(index=name, ignore_unavailable=True)

    def insert_document(self, body):
        return self.es.index(index=self.index_name, body=body)
    
    def delete_document(self, doc_id):
        try:
            response = self.es.delete(index=self.index_name, id=doc_id)
            print(f"Document {doc_id} deleted from index {self.index_name}.")
            return response
        except NotFoundError:
            print(f"Document {doc_id} not found in index {self.index_name}.")
            return None

    def insert_documents(self, documents):
        operations = []
        for document in documents:
            operations.append({'index': {'_index': self.index_name}})
            operations.append(document)
        return self.es.bulk(operations=operations)
    
    def reindex(self):
        self.create_index()
        with open('data.json', 'rt') as f:
            documents = json.loads(f.read())
        return self.insert_documents(documents)
    
    def search(self, **query_args):
        return self.es.search(index=self.index_name, **query_args)

    def retrieve_document(self, id):
        return self.es.get(index=self.index_name, id=id)