import re

from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import DensePassageRetriever, FARMReader
from haystack.pipelines import ExtractiveQAPipeline
from haystack.utils import print_answers

from src.helper import load_json

# Load JSON data
data = load_json("output/greenday_lyrics_preprocessed.json")

# Proper format: 
'''
docs = [
    {
        'content': DOCUMENT_TEXT_HERE,
        'meta': {'name': DOCUMENT_NAME, ...}
    }, ...
]
'''
# replace all newline characters with a space (still needed?)
for song_name, lyrics in data.items():
    data[song_name] = lyrics.replace('\n', ' ')
    # remove everything that is in [] brackets and the brackets themselves
    data[song_name] = re.sub(r'\[.*?\]', '', data[song_name])

# Create a list of documents
documents = []
for song_name, lyrics in data.items():
    documents.append({"content": lyrics, "meta": {"song_name": song_name}})

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
    "21 guns",
    "american idiot",
]

for question in questions:
    prediction = pipeline.run(query=question, params={"Retriever": {"top_k": 10}, "Reader": {"top_k": 3}})
    print_answers(prediction, details="minimum")
