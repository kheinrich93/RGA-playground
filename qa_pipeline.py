import re
from typing import List

from haystack import Document, Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.components.readers import ExtractiveReader

from src.helper import load_json

class NLP_pipeline():
    def __init__(self) -> None:
        pass

    def load_data(self, json_path:str):
        # Load JSON data
        self.data = load_json(json_path)
        # replace all newline characters with a space (still needed?)
        for song_name, lyrics in self.data.items():
            self.data[song_name] = lyrics.replace('\n', ' ')
            # remove everything that is in [] brackets and the brackets themselves
            self.data[song_name] = re.sub(r'\[.*?\]', '', self.data[song_name])

    def create_embeddings_with_retriever(self):
        # Create documents with correct format 
        documents = [Document(content=lyrics, meta={"title": title}) for title, lyrics in self.data.items()]

        # Initialize the Document Store and its embedding
        self.document_store = InMemoryDocumentStore()
        doc_embedder = SentenceTransformersDocumentEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")
        doc_embedder.warm_up()

        # Apply embeddings
        docs_with_embeddings = doc_embedder.run(documents)
        self.document_store.write_documents(docs_with_embeddings["documents"])

        self.retriever = InMemoryEmbeddingRetriever(self.document_store)

    def create_text_embedder(self):
        # prompt/query embedding
        self.text_embedder = SentenceTransformersTextEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")


    def create_extractive_pipeline(self):
        # Create reader for output
        self.reader = ExtractiveReader()
        self.reader.warm_up()

        # Create pipeline components
        self.extractive_qa_pipeline = Pipeline()
        
        self.extractive_qa_pipeline.add_component(instance=self.text_embedder, name="text_embedder")
        self.extractive_qa_pipeline.add_component(instance=self.retriever , name="retriever")
        self.extractive_qa_pipeline.add_component(instance=self.reader, name="reader")

        # Connect components
        self.extractive_qa_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
        self.extractive_qa_pipeline.connect("retriever.documents", "reader.documents")

    def run_extractive_pipeline(self, query:List):
        for q in query:
            result = self.extractive_qa_pipeline.run(
                data={"text_embedder": {"text": q}, "retriever": {"top_k": 3}, "reader": {"query": q, "top_k": 2}})
            print(result)


NLP_pipeline = NLP_pipeline()
NLP_pipeline.load_data("output/greenday_lyrics_preprocessed.json")
NLP_pipeline.create_embeddings_with_retriever()
NLP_pipeline.create_text_embedder()
NLP_pipeline.create_extractive_pipeline()


# Ask questions
query = [
    "21 guns",
    "american idiot",
]
NLP_pipeline.run_extractive_pipeline(query)