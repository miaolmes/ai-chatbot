from langchain.document_loaders import TextLoader, PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from chatbot.config import get_settings
import os
from typing import Optional


class DocumentEventHandler(FileSystemEventHandler):
    def __init__(self, indexer):
        self.indexer = indexer

    def on_created(self, event):
        if not event.is_directory:
            self.indexer.index_document(event.src_path)

    def on_modified(self, event):
        pass  # Ignore modification events to prevent double indexing


class Indexer:
    def __init__(self):
        self.settings = get_settings()
        self.embeddings = OpenAIEmbeddings(
            openai_api_base=self.settings.openai_api_base,
            openai_api_key=self.settings.openai_api_key
        )
        self.vector_store = Chroma(
            collection_name='documents',
            persist_directory=self.settings.chatbot_vector_store,
            embedding_function=self.embeddings
        )
        self.observer: Optional[Observer] = None

    def start(self):
        event_handler = DocumentEventHandler(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.settings.chatbot_doc_store, recursive=True)
        self.observer.start()

        # Index existing documents
        for filename in os.listdir(self.settings.chatbot_doc_store):
            filepath = os.path.join(self.settings.chatbot_doc_store, filename)
            if os.path.isfile(filepath):
                self.index_document(filepath)

    def stop(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()

    def index_document(self, filepath: str):
        try:
            # Select loader based on file extension
            if filepath.endswith('.pdf'):
                loader = PyMuPDFLoader(filepath)
            else:
                loader = TextLoader(filepath)

            documents = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(documents)

            # Add to vector store
            self.vector_store.add_documents(splits)
            self.vector_store.persist()
            print(f"Indexed document: {filepath}")
        except Exception as e:
            print(f"Error indexing document {filepath}: {str(e)}")
