from whoosh.fields import Schema, TEXT, ID, KEYWORD, STORED
from whoosh.index import create_in
from whoosh.analysis import StemmingAnalyzer, CharsetFilter, LowercaseFilter, SimpleAnalyzer
from whoosh.support.charset import accent_map

import os

custom_analyzer = SimpleAnalyzer()


def create_schema():
    return Schema(
        title=ID(stored=True, unique=True),
        content=TEXT(analyzer=custom_analyzer),
        categories=KEYWORD(commas=True, scorable=True, analyzer=LowercaseFilter()),
        redirects=STORED,
    )


def create_index(index_dir, schema):
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)
    return create_in(index_dir, schema)


def add_documents_to_index(indexer, articles):
    writer = indexer.writer()

    for article in articles:
        writer.add_document(
            title=article["title"],
            content=article["content"],
            categories=article["categories"],
            redirects=article["redirects"],
        )

    writer.commit()
