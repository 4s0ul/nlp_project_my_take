FROM python:3.12-slim

WORKDIR /app
COPY dictionary /app/dictionary
COPY pyproject.toml /app/
COPY README.md /app/
    
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu . \
    && python -m nltk.downloader punkt stopwords punkt_tab \
    && python -m spacy download en_core_web_md \
    && python -m spacy download ru_core_news_md \
    && python -c "import stanza; stanza.download('en'); stanza.download('ru')"

ENTRYPOINT ["python", "./dictionary/main.py"]
