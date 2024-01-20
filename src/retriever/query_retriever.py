from whoosh.query import And, Or, Not, Term

import spacy

nlp = spacy.load("en_core_web_sm")


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


def build_boolean_query_from_clue(clue, category=None):
    # doc = nlp(clue)
    #
    # key_phrases = [chunk.text for chunk in doc.noun_chunks]
    # named_entities = [ent.text for ent in doc.ents]
    #
    # category_term = category.lower().replace(' ', '_')
    #
    # category_query = Term('categories', category_term)
    # content_queries = [Term('content', term) for term in key_phrases + named_entities]
    #
    # if content_queries:
    #     query = And([category_query, Or(content_queries)])
    # else:
    #     query = category_query
    #
    # return query
    # doc = nlp(clue)
    #
    # # Extract key phrases and named entities
    # key_phrases = [chunk.text for chunk in doc.noun_chunks]
    # named_entities = [ent.text for ent in doc.ents]
    #
    # # Additional processing based on category
    # # For example, if category implies a person, prioritize person entities
    # if "CELEBRITY" in category or "AUTHOR" in category:
    #     named_entities = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    #
    # # Combine key phrases and named entities for the content query
    # content_terms = set(key_phrases + named_entities)
    #
    # # Construct Boolean queries
    # category_query = Term('categories', category.lower().replace(' ', '_'))
    # content_queries = [Term('content', term) for term in content_terms]
    #
    # # Combine queries
    # if content_queries:
    #     combined_query = And([category_query, Or(content_queries)])
    # else:
    #     combined_query = category_query
    #
    # return combined_query

    must_terms, should_terms, not_terms = analyze_clue(clue, category)

    must_queries = And([Term('content', term) for term in must_terms])
    should_queries = Or([Term('content', term) for term in should_terms])
    not_queries = Not([Term('content', term) for term in not_terms])

    final_query = must_queries
    if should_queries and len(should_terms) != 0:
        final_query = final_query & should_queries
    if not_queries and len(not_terms) != 0:
        final_query = final_query & not_queries

    return final_query


def analyze_clue(clue, category=None):
    doc = nlp(clue)
    must_terms = []
    should_terms = [category] if category else []
    not_terms = []

    for ent in doc.ents:
        must_terms.append(ent.text)

    for token in doc:
        if token.pos_ in ["ADJ", "NOUN"] and token.text not in must_terms:
            should_terms.append(token.text)
        elif token.dep_ == "neg":
            not_terms.append(token.head.text)

    return must_terms, should_terms, not_terms
