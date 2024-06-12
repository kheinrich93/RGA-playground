import json
import re

from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import DensePassageRetriever, FARMReader
from haystack.pipelines import ExtractiveQAPipeline
from haystack.utils import clean_wiki_text, convert_files_to_docs, fetch_archive_from_http, print_answers

# bring data into proper format: 
'''
docs = [
    {
        'content': DOCUMENT_TEXT_HERE,
        'meta': {'name': DOCUMENT_NAME, ...}
    }, ...
]
'''



# Load your JSON data
with open("output\greenday_lyrics.json", "r") as file:
    data = json.load(file)

# replace all newline characters with a space
for url, lyrics in data.items():
    data[url] = lyrics.replace('\n', ' ')
    # remove everything that is in [] brackets and the brackets themselves
    data[url] = re.sub(r'\[.*?\]', '', data[url])

# Create a list of documents
documents = []
for url, lyrics in data.items():
    documents.append({"content": lyrics, "meta": {"url": url}})

# Initialize the Document Store
document_store = InMemoryDocumentStore()

# Write documents to the Document Store
document_store.write_documents(documents)

# Initialize the Retriever
retriever = DensePassageRetriever(
    document_store=document_store,
    query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
    passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base"
)

# Update embeddings
document_store.update_embeddings(retriever)

# Initialize the Reader
reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2")

# Create the pipeline
pipeline = ExtractiveQAPipeline(reader, retriever)

# Ask questions
questions = [
    "What is '21 guns' about?",
    "What is 'american idiot' about?",
]

for question in questions:
    prediction = pipeline.run(query=question, params={"Retriever": {"top_k": 10}, "Reader": {"top_k": 3}})
    print_answers(prediction, details="minimum")
