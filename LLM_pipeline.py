import re
from typing import List

from haystack import Document, Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever, InMemoryEmbeddingRetriever
from haystack.components.joiners import DocumentJoiner
from haystack.components.rankers import TransformersSimilarityRanker
from haystack.components.readers import ExtractiveReader
from haystack.components.builders import PromptBuilder

from src.groq_model import GroqGenerator
from src.helper import load_json, get_api_token, print_pretty_results, output_pipeline_as_yaml


# TODO: 
'''
- improve pipeline building: https://haystack.deepset.ai/tutorials/29_serializing_pipelines
- try other document stores -> DB!
- create general output print
'''

class NLP_pipeline():
    def __init__(self) -> None:
        # Initialize the Document Store and its embedding
        self.document_store = InMemoryDocumentStore()

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

        # Prepare indexing pipeline
        doc_embedder = SentenceTransformersDocumentEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")
        doc_embedder.warm_up()

        # Apply embeddings
        docs_with_embeddings = doc_embedder.run(documents)
        self.document_store.write_documents(docs_with_embeddings["documents"])

        self.bm25_retriever = InMemoryBM25Retriever(self.document_store)
        self.embedding_retriever = InMemoryEmbeddingRetriever(self.document_store)

        # for hybrid retrieval
        self.document_joiner = DocumentJoiner()
        self.ranker = TransformersSimilarityRanker(model="BAAI/bge-reranker-base")

    def create_text_embedder(self):
        # prompt/query embedding
        self.text_embedder = SentenceTransformersTextEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")

    def create_prompt_builder(self):
        # Create a custom prompt with prompt builder
        template = """
        Create song lyrics similar to {{question}} and use the following lyrics as context:
        {% for document in documents %}
            {{ document.content }}
        {% endfor %}
        """

        self.prompt_builder = PromptBuilder(template=template)
    
    def create_llm_generator(self):
        self.llm_generator = GroqGenerator(get_api_token("auth_tokens/groq.json"))

    def create_hybrid_extractive_pipeline(self, plot_pipeline:bool = False, output_pipeline:bool = True):
        # Create pipeline components
        self.hybrid_extractive_qa_pipeline = Pipeline()
        
        self.hybrid_extractive_qa_pipeline.add_component(instance=self.text_embedder, name="text_embedder")
        self.hybrid_extractive_qa_pipeline.add_component(instance=self.embedding_retriever , name="embedding_retriever")
        self.hybrid_extractive_qa_pipeline.add_component(instance=self.bm25_retriever , name="bm25_retriever")
        self.hybrid_extractive_qa_pipeline.add_component(instance=self.document_joiner, name="document_joiner")
        self.hybrid_extractive_qa_pipeline.add_component(instance=self.ranker, name="ranker")

        # Connect components
        self.hybrid_extractive_qa_pipeline.connect("text_embedder", "embedding_retriever")
        self.hybrid_extractive_qa_pipeline.connect("bm25_retriever", "document_joiner")
        self.hybrid_extractive_qa_pipeline.connect("embedding_retriever", "document_joiner")
        self.hybrid_extractive_qa_pipeline.connect("document_joiner", "ranker")

        output_pipeline_as_yaml(self.hybrid_extractive_qa_pipeline, "pipelines/hybrid_qa_pipeline.yaml") if output_pipeline else None
        self.hybrid_extractive_qa_pipeline.draw("hybrid_extractive_qa_pipeline.png") if plot_pipeline else None


    def create_extractive_pipeline(self, plot_pipeline:bool = False, output_pipeline:bool = True):
        # Create reader for output
        self.reader = ExtractiveReader()
        self.reader.warm_up()

        # Create pipeline components
        self.extractive_qa_pipeline = Pipeline()
        
        self.extractive_qa_pipeline.add_component(instance=self.text_embedder, name="text_embedder")
        self.extractive_qa_pipeline.add_component(instance=self.embedding_retriever , name="embedding_retriever")
        self.extractive_qa_pipeline.add_component(instance=self.reader, name="reader")

        # Connect components
        self.extractive_qa_pipeline.connect("text_embedder", "embedding_retriever")
        self.extractive_qa_pipeline.connect("embedding_retriever.documents", "reader.documents")

        output_pipeline_as_yaml(self.extractive_qa_pipeline, "pipelines/extractive_qa_pipeline.yaml") if output_pipeline else None
        self.extractive_qa_pipeline.draw("extractive_qa_pipeline.png") if plot_pipeline else None

    def create_rag_pipeline(self, plot_pipeline:bool = False, output_pipeline:bool = True):
        # Create pipeline components
        self.rag_pipeline = Pipeline()

        self.rag_pipeline.add_component(instance=self.text_embedder, name="text_embedder")
        self.rag_pipeline.add_component(instance=self.embedding_retriever , name="embedding_retriever")
        self.rag_pipeline.add_component(instance=self.prompt_builder, name = "prompt_builder")
        self.rag_pipeline.add_component(instance=self.llm_generator, name="generator")

        # Connect components
        self.rag_pipeline.connect("text_embedder.embedding", "embedding_retriever.query_embedding")
        self.rag_pipeline.connect("embedding_retriever", "prompt_builder.documents")
        self.rag_pipeline.connect("prompt_builder", "generator")


        output_pipeline_as_yaml(self.rag_pipeline, "pipelines/rag_pipeline.yaml") if output_pipeline else None
        self.rag_pipeline.draw("rag_pipeline.png") if plot_pipeline else None


    def run_extractive_pipeline(self, query:List):
        responses = []
        for q in query:
            response = self.extractive_qa_pipeline.run(
                data={"text_embedder": {"text": q},
                                        "reader": {"query": q, "top_k": 3}})

            responses.append(response)

        print(responses)


    def run_hybrid_extractive_pipeline(self, query:List):
        responses = []
        for q in query:
            response = self.hybrid_extractive_qa_pipeline.run(
                                        {"text_embedder": {"text": q}, "bm25_retriever": {"query": q}, "ranker": {"query": q, "top_k": 3}})
            
            responses.append(response)

        print(responses)

    def run_rag_pipeline(self, query:List):
        responses = []
        for q in query:
            response = self.rag_pipeline.run({"text_embedder": {"text": q}, 
                                            "embedding_retriever": {"top_k": 3},
                                            "prompt_builder": {"question": q}})
            responses.append(response)

        print_pretty_results(query, responses)


query = [
    "21 guns",
    "american idiot",
]
NLP_pipeline = NLP_pipeline()
# --- data loading and embedding creation ---
NLP_pipeline.load_data("output/greenday_lyrics_preprocessed.json")
NLP_pipeline.create_embeddings_with_retriever()
NLP_pipeline.create_text_embedder()

# --- qa pipeline ---
# NLP_pipeline.create_extractive_pipeline()
# NLP_pipeline.run_extractive_pipeline(query)

# --- hybrid qa pipeline ---
# NLP_pipeline.create_hybrid_extractive_pipeline()
# NLP_pipeline.run_hybrid_extractive_pipeline(query)

# --- RAG pipeline ---
# create prompt list that contains song with the following text around it "create song lyrics similar to [song]"
NLP_pipeline.create_prompt_builder()
NLP_pipeline.create_llm_generator()
NLP_pipeline.create_rag_pipeline()
NLP_pipeline.run_rag_pipeline(query)

