from whoosh.qparser import QueryParser
from whoosh.index import open_dir

from openai import OpenAI

openai_api_key = "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"


client = OpenAI(api_key=openai_api_key)


def search_index(query_str, category, with_rerank=False, index_dir="path/to/index"):
    ix = open_dir(index_dir)
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(query_str)
        results = searcher.search(query, limit=10)

        titles = [hit.field()["title"] for hit in results]
        if not with_rerank:
            return titles

        ranked_results = gpt3_rerank(titles, query_str, category)

        return ranked_results


def gpt3_complete(clue, category):
    prompt = (
        f"Given a Jeopardy clue '{clue}' in the category '{category}', "
        "which returned no initial search results, suggest a more general query. "
        "Include related terms or broader concepts that could help find relevant information "
        "in a comprehensive knowledge database."
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a search engine assistant."},
            {"role": "user", "content": f"Question: {prompt}"}
        ]
    )

    enhanced_query = response.choices[0].message.content
    return enhanced_query


def gpt3_rerank(titles, clue, category):
    # Building a detailed prompt
    prompt = (
        f"Rank the following options based on their relevance to the Jeopardy clue '{clue}' "
        f"and the category '{category}'. Consider which of these would be most likely to contain "
        "the correct answer:\n\n"
        + "\n".join([f"{title}" for title in titles])
        + "\n\nProvide a ranked list of the titles based on relevance."
          " The output must provide only the titles with the most relevant first, separated by newlines. Do not number the list."
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a search engine assistant."},
            {"role": "user", "content": f"Question: {prompt}"}
        ]
    )

    ranked_list = response.choices[0].message.content.strip().split("\n")

    return ranked_list


def calculate_precision_at_1(search_results, correct_answer):
    if not search_results:
        return 0
    return 1 if search_results[0] == correct_answer else 0


def calculate_mrr(search_results, correct_answer):
    for i, result in enumerate(search_results, start=1):
        if result == correct_answer:
            return 1 / i
    return 0
