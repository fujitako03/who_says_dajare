from google.cloud import language_v1
from google.cloud.language_v1 import enums
import six
import pandas as pd
import csv


def sample_analyze_sentiment(content):

    client = language_v1.LanguageServiceClient()

    # content = 'Your text to analyze, e.g. Hello, world!'

    if isinstance(content, six.binary_type):
        content = content.decode('utf-8')

    type_ = enums.Document.Type.PLAIN_TEXT
    document = {'type': type_, 'content': content}

    response = client.analyze_sentiment(document)
    sentiment = response.document_sentiment

    return {"score": sentiment.score, "magnitude": sentiment.magnitude}


def insert_to_csv(row, filename):
    with open(filename, 'a') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(row)
        f.close()


if __name__ == '__main__':
    dajare_df = pd.read_csv("./data/dajare.tsv", sep="\t")

    for index, row in dajare_df.iterrows():

        api_scores = sample_analyze_sentiment(row.text)

        row = [row.dajare_id, api_scores["score"], api_scores["magnitude"]]
        insert_to_csv(row, "./data/sentiment.csv")

