import re
from flask import Flask, render_template, request, jsonify, abort
from search import Search
import fitz
import click
from datetime import date, datetime

app = Flask(__name__)
mapping = {
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
index_name = 'research_documents'
es = Search(mapping, index_name)

@app.get('/')
def index():
    return render_template('index.html')

@app.post('/upload_file')
def handle_file_upload():
    form = request.form
    file = request.files['file']
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']
    
    # Check if the file is a PDF
    if file.filename == '':
        return "No selected file", 400
    if not file.filename.endswith('.pdf'):
        return "Please upload a PDF file", 400

    # Read PDF content
    pdf_text = extract_text_from_pdf(file)
    try:
        body = {
            'title': form.get('title', ''),
            'filename': file.filename,
            'author': form.get('author', ''),
            'content': pdf_text,
            'tags': form.get('tags', ''),
            'publication_date': form.get('publication_date'),
            'platform': form.get('platform')
        }
        es.insert_document(body)
        return 'Inserted Successfully', 200
    except Exception as e:
        print(e)
        return 'Failed to Process', 500

def extract_text_from_pdf(file):
    pdf_text = ""
    # Open the uploaded PDF file with PyMuPDF
    pdf_document = fitz.open(stream=file.read(), filetype="pdf")
    
    # Iterate over each page and extract text
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        pdf_text += page.get_text("text")  # Extract text in plain text format

    pdf_document.close()
    return pdf_text

@app.post('/')
def handle_search():
    query = request.form.get('query', '')
    filters, parsed_query = extract_filters(query)
    from_ = request.form.get('from_', type=int, default=0)

    if parsed_query:
        search_query = {
            'must': {
                'multi_match': {
                    'query': parsed_query,
                    'fields': ['title', 'content'],
                }
            }
        }
    else:
        search_query = {
            'must': {
                'match_all': {}
            }
        }

    results = es.search(
        query={
            'bool': {
                **search_query,
                **filters
            }
        },
        aggs={
            'platform-agg': {
                'terms': {
                    'field': 'platform',
                }
            },
            'author-agg': {
                'terms': {
                    'field': 'author',
                }
            },
            'year-agg': {
                'date_histogram': {
                    'field': 'publication_date',
                    'calendar_interval': 'year',
                    'format': 'yyyy',
                },
            },
        },
        highlight={
            "fields": {
                "content": {
                    "fragment_size": 500, 
                    "number_of_fragments": 3
                }
            },
            "pre_tags": ["<mark>"], 
            "post_tags": ["</mark>"],
            "max_analyzed_offset":1000000,
        },
        size=5,
        from_=from_
    )

    aggs = {
        'Author': {
            bucket['key']: bucket['doc_count']
            for bucket in results['aggregations']['author-agg']['buckets']
            if bucket['doc_count'] > 0
        },
        'Platform': {
            bucket['key']: bucket['doc_count']
            for bucket in results['aggregations']['platform-agg']['buckets']
            if bucket['doc_count'] > 0
        },
        'Year': {
            bucket['key_as_string']: bucket['doc_count']
            for bucket in results['aggregations']['year-agg']['buckets']
            if bucket['doc_count'] > 0
        },
    }
    for idx in range(len(results['hits']['hits'])):
        hit = results['hits']['hits'][idx]
        original_content = hit['_source']['content']
        
        # Get highlighted fragments and combine them inline
        highlighted_fragments = hit['highlight']['content'] if 'highlight' in hit else []
        highlighted_content_inline = original_content  # Start with the original content

        # Replace matched terms inline with highlighted terms
        highlighted_fragments.sort(key=lambda x: len(x), reverse=True)
        for fragment in highlighted_fragments:
            # Remove <mark> tags for regex compatibility, then escape for regex search
            fragment_text = re.sub(r'<\/?mark>', '', fragment)
            highlighted_content_inline = re.sub(re.escape(fragment_text), fragment, highlighted_content_inline, flags=re.IGNORECASE)
        results['hits']['hits'][idx]['highlighted_content_inline'] = highlighted_content_inline


    return render_template('index.html', results=results['hits']['hits'],
                           query=query, from_=from_,
                           total=results['hits']['total']['value'], aggs=aggs)

@app.get('/document/<id>')
def get_document(id):
    document = es.retrieve_document(id)
    title = document['_source']['title']
    tags = document['_source']['tags']
    publication_date = document['_source']['publication_date']
    author = document['_source']['author']
    filename = document['_source']['filename']
    paragraphs = document['_source']['content'].split('\n')
    platform = document['_source']['platform']
    return render_template('document.html', title=title, paragraphs=paragraphs, tags=tags, publication_date=publication_date, author=author, filename=filename, platform=platform)

@app.delete('/document/<id>')
def delete_document(id):
    es.delete_document(id)
    return 'Document Deleted!', 200

@app.cli.command()
def reindex():
    """Regenerate the Elasticsearch index."""
    response = es.reindex()
    print(f'Index with {len(response["items"])} documents created '
          f'in {response["took"]} milliseconds.')
    
@app.cli.command()
@click.option('--name', required=True, help='The index name to delete.')
def delete_index(name):
    es.delete_index(name)
    print('Index deleted!!')

@app.cli.command()
@click.option('--name', help='The index name to delete.')
def create_index(name):
    es.create_index(name)
    print('Index created!!')

def extract_filters(query):
    filters = []

    filter_regex = r'platform:\s*\'([^"]+)\''
    m = re.search(filter_regex, query)
    if m:
        filters.append({
            'term': {
                'platform': {
                    'value': m.group(1)
                }
            },
        })
        query = re.sub(filter_regex, '', query).strip()

    filter_regex = r'author:\s*\'([^"]+)\''
    m = re.search(filter_regex, query)
    if m:
        filters.append({
            'term': {
                'author': {
                    'value': m.group(1)
                }
            },
        })
        query = re.sub(filter_regex, '', query).strip()

    filter_regex = r'year:\s*\'([^"]+)\''
    m = re.search(filter_regex, query)
    if m:
        filters.append({
            'range': {
                'publication_date': {
                    'gte': f'{m.group(1)}||/y',
                    'lte': f'{m.group(1)}||/y',
                }
            },
        })
        query = re.sub(filter_regex, '', query).strip()

    return {'filter': filters}, query