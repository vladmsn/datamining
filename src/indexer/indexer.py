from whoosh.analysis import RegexTokenizer, LowercaseFilter, Filter, StopFilter
from whoosh.fields import Schema, TEXT, ID, KEYWORD, STORED
from whoosh.index import create_in
import spacy
import os

# Load the spaCy English language model
nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])


def lemmatize_content_in_batches(articles, batch_size=100):
    batch = []  # Temporary list to collect articles for the current batch
    no_of_batches = 0

    # Iterate over each article in the generator
    for article in articles:
        batch.append(article)  # Add the current article to the batch

        # Check if the batch is full
        if len(batch) >= batch_size:
            # Process the full batch
            texts = [article["content"] for article in batch]
            processed_docs = list(nlp.pipe(texts))
            no_of_batches += 1

            # Update the article content with lemmatized text
            for article, doc in zip(batch, processed_docs):
                article["content"] = " ".join(token.lemma_ for token in doc)
                yield article  # Yield the updated article

            batch = []  # Reset the batch list for the next set of articles

    # Process any remaining articles in the last batch (if any)
    if batch:
        no_of_batches += 1
        texts = [article["content"] for article in batch]
        processed_docs = list(nlp.pipe(texts))

        # Update the article content with lemmatized text
        for article, doc in zip(batch, processed_docs):
            article["content"] = " ".join(token.lemma_ for token in doc)
            yield article  # Yield the updated article

    print(f"Processed {no_of_batches} batches.")


def custom_analyzer():
    return RegexTokenizer() | LowercaseFilter() | StopFilter()


def create_schema():
    return Schema(
        title=ID(stored=True, unique=True),
        content=TEXT(analyzer=custom_analyzer()),
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
