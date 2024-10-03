from typing import Any
import os
import pandas as pd
from pymongo.mongo_client import MongoClient
import json
from ensure import ensure_annotations


class mongo_operation:
    __collection = None  # private/protected variable
    __database = None

    def __init__(self, client_url: str, database_name: str, collection_name: str = None):
        self.client_url = client_url
        self.database_name = database_name
        self.collection_name = collection_name

    def create_mongo_client(self):
        client = MongoClient(self.client_url)
        return client

    def create_database(self):
        if mongo_operation.__database is None:
            client = self.create_mongo_client()
            mongo_operation.__database = client[self.database_name]
        return mongo_operation.__database

    def create_collection(self, collection=None):
        if collection:
            self.collection_name = collection

        if mongo_operation.__collection is None:
            database = self.create_database()
            mongo_operation.__collection = database[self.collection_name]

        if mongo_operation.__collection != self.collection_name:
            database = self.create_database()
            mongo_operation.__collection = database[self.collection_name]

        return mongo_operation.__collection

    def insert_record(self, record: dict, collection_name: str) -> Any:
        collection = self.create_collection(collection_name)

        if isinstance(record, list):
            for data in record:
                if not isinstance(data, dict):
                    raise TypeError("Each record must be a dictionary")
            collection.insert_many(record)
        elif isinstance(record, dict):
            collection.insert_one(record)

    def bulk_insert(self, datafile, collection_name: str = None):
        self.path = datafile

        # Read the file based on its extension
        if self.path.endswith('.csv'):
            dataframe = pd.read_csv(self.path, encoding='utf-8')

        elif self.path.endswith(".xlsx"):
            dataframe = pd.read_excel(self.path, encoding='utf-8')

        else:
            raise ValueError("Unsupported file type. Please provide a CSV or XLSX file.")

        # Convert DataFrame to a list of dictionaries
        datajson = dataframe.to_dict(orient='records')

        # Insert the data into MongoDB
        collection = self.create_collection(collection_name)
        collection.insert_many(datajson)
