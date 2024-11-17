import json
from pprint import pprint
from dotenv import load_dotenv
from elasticsearch import Elasticsearch, NotFoundError

load_dotenv()

ES_HOST = "https://localhost:9200"
ES_USERNAME = "elastic"
ES_PASSWORD = "tTY-*Red_Tui+sMTpvyc"
INDEX_NAME = "research_documents"

class Search:
    def __init__(self):
        # self.es = Elasticsearch(cloud_id=os.environ['ELASTIC_CLOUD_ID'], api_key=os.environ['ELASTIC_API_KEY'])
        self.es = Elasticsearch(ES_HOST, basic_auth=(ES_USERNAME, ES_PASSWORD), ca_certs='http_ca.crt')
        self.index_name = INDEX_NAME
        self.mapping = {
            "mappings": {
                "properties": {
                    "title": {"type": "text"},
                    "filename": {"type": "text"},
                    "author": {"type": "keyword"},
                    "content": {"type": "text"},
                    "tags": {"type": "keyword"},
                    "publication_date": {"type": "date"},
                    "platform": {"type": "keyword"}
                }
            }
        }
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

    def insert_document(self, title, filename, author, content, tags, publication_date, platform):
        document = {
            'title': title,
            'filename': filename,
            'author': author,
            'content': content,
            'tags': tags,
            'publication_date': publication_date,
            'platform': platform
        }
        return self.es.index(index=self.index_name, body=document)
    
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