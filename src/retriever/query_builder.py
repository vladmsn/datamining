import spacy

nlp = spacy.load("en_core_web_sm")


def preprocess_clue(clue):
    # Process the clue with spaCy
    doc = nlp(clue)

    # Extract lemmatized forms of tokens, excluding stop words and punctuation
    processed_tokens = [
        token.lemma_ for token in doc if not token.is_stop and not token.is_punct
    ]

    # Join the processed tokens back into a string query
    processed_query = " ".join(processed_tokens)

    return processed_query


def build_query_from_clue(clue):
    doc = nlp(clue)

    # Extract named entities, noun chunks, verbs, and adjectives
    entities = [ent.text for ent in doc.ents]
    noun_chunks = [chunk.text for chunk in doc.noun_chunks]
    # verbs_adjectives = [token.text for token in doc if token.pos_ in ['VERB', 'ADJ'] and not token.is_stop] - improvement of +4 % accuracy if omitted

    # Combine all extracted elements
    all_terms = set(entities + noun_chunks)

    # Construct the query string
    # Simple concatenation for Whoosh's QueryParser
    query = " ".join(all_terms)

    return query
