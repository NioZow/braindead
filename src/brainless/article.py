from newspaper import Article


def get_article_content(url: str) -> str:
    article = Article(url)
    article.download()
    article.parse()
    return article.text
