import re


def parse_wikipedia_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        current_article = None
        tpl_regex = re.compile(r"\[tpl].*?\[/tpl]")

        for line in file:
            line = tpl_regex.sub("", line)

            if line.startswith("[[") and line.endswith("]]\n"):
                if current_article:
                    yield current_article
                title = line[2:-3]
                current_article = {
                    "title": title,
                    "content": "",
                    "categories": [],
                    "redirects": [],
                }
            elif line.startswith("CATEGORIES:"):
                categories = line[len("CATEGORIES:"):].strip().split(", ")
                if current_article:
                    current_article["categories"] = categories
            elif line.startswith("#REDIRECT"):
                redirects = [
                    redirect.strip() for redirect in line[len("#REDIRECT"):].split("#")
                ]
                if current_article:
                    current_article["redirects"] = redirects
            elif current_article is not None:
                current_article["content"] += line

        if current_article:
            yield current_article
