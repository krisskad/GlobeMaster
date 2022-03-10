from API.models import *
import pandas as pd
import nltk
from nameparser.parser import HumanName
from nltk.corpus import wordnet
import os
from django.conf import settings
from glob import glob
from nltk.sentiment import SentimentIntensityAnalyzer
import locationtagger

##########################
nltk.data.path.append(os.path.join(settings.BASE_DIR, 'storage'))
# nltk.download("all", download_dir=os.path.join(settings.BASE_DIR, 'storage'))
##########################
dir_lib = []
root = os.path.join(settings.BASE_DIR, 'storage')
for path, subdirs, files in os.walk(root):
    for name in subdirs:
        dir_lib.append(os.path.join(path, name))

req_lib = ["punkt", "averaged_perceptron_tagger",
           "maxent_ne_chunker", "words", "wordnet", "vader_lexicon",
           "treebank", "maxent_treebank_pos_tagger"]
# try:
#     nltk.data.find('tokenizers/punkt')
#     nltk.data.find('tokenizers/punkt')
#     nltk.data.find('tokenizers/punkt')
#     nltk.data.find('tokenizers/punkt')
#     nltk.data.find('tokenizers/punkt')
# except LookupError:
#     nltk.download('punkt', download_dir=os.path.join(settings.BASE_DIR, 'storage'))

for req in req_lib:
    flag = False
    for dir in dir_lib:
        if req in dir:
            flag = True
            # print(req)
            break
    if flag is False:
        nltk.download(req, download_dir=os.path.join(settings.BASE_DIR, 'storage'))


def upload_timeseries(df):
    pass


STOPWORDS = {'doing', '—', '-', '_', 'at', '”', 'could', 'mr.', ',', '.', '?', '"', '/', 'haven', 'themselves', 'mustn', 'won', 'out', 'will', 'himself', 'its', 'can', 'both', 'yours', 'once', "needn't", 'hasn', 'more', 'yourselves', 'he', 'again', 'no', "isn't", 'she', 'herself', 'but', 'myself', 'ourselves', 'just', "it's", 'yourself', 'what', 'y', 'ain', 'ours', 'weren', 'own', "you've", 'now', 'that', 'any', "don't", 'being', "shouldn't", 'having', 's', 'off', 'each', 'through', 'few', 'at', 'wouldn', 'me', "that'll", 'against', 'd', 'been', 'all', 'than', 'on', "you'd", 'is', 'or', 'by', 'isn', 'for', "weren't", 'a', 'am', 'then', 'some', 'before', 'down', "couldn't", 'them', 're', 'him', 'aren', "doesn't", 'so', 'which', "hadn't", 'did', "shan't", 'over', 'hers', 'into', 'theirs', 've', 'm', 'further', 'my', 'an', 'when', 'our', 'of', 'in', 'very', 'don', "aren't", "didn't", 'be', 'too', 'whom', 'during', 'where', 'have', 'with', "she's", 'wasn', 'are', 't', "mustn't", 'above', 'itself', 'does', 'who', 'why', 'while', 'not', 'their', 'this', 'if', 'same', "should've", 'after', 'hadn', 'didn', 'you', 'about', 'how', 'it', 'had', 'o', 'here', 'other', 'under', 'until', 'most', 'we', 'your', 'because', 'and', 'has', 'i', 'ma', 'll', 'they', 'shan', 'his', "haven't", 'was', 'up', 'from', 'those', 'couldn', "won't", 'needn', 'her', 'mightn', 'to', 'should', "mightn't", 'doesn', 'were', "wasn't", 'shouldn', "wouldn't", 'the', 'do', "you'll", 'as', 'between', 'nor', 'these', 'there', 'below', 'such', "hasn't", "you're", 'only'}


def get_word_freq(df):
    # df["raw"] = df["title"] + " " + df["content"]

    df['text'] = df['title'].apply(
        lambda x: ' '.join([word for word in set(x.split(" ")) if word.lower() not in STOPWORDS]))
    # print(df)
    res = df.text.str.split(expand=True).stack().value_counts()
    # print(res.to_frame())
    kwd = pd.DataFrame(res).reset_index()
    kwd.columns = ['text', 'value']
    return kwd


def get_human_names(text):
    person_list = []
    tokens = nltk.tokenize.word_tokenize(text)
    pos = nltk.pos_tag(tokens)
    sentt = nltk.ne_chunk(pos, binary = False)

    person = []
    name = ""
    for subtree in sentt.subtrees(filter=lambda t: t.label() == 'PERSON'):
        for leaf in subtree.leaves():
            person.append(leaf[0])
        if len(person) > 1: #avoid grabbing lone surnames
            for part in person:
                name += part + ' '
            if name[:-1] not in person_list:
                person_list.append(name[:-1])
            name = ''
        person = []
    return person_list


def get_sentiment(text):
    sia = SentimentIntensityAnalyzer()
    return sia.polarity_scores(text)


def get_location(text):
    # extracting entities.
    place_entity = locationtagger.find_locations(text=text)

    # getting all countries
    return {
        "country": place_entity.countries,
        "state": place_entity.regions,
        "city": place_entity.cities
    }
    #
    # if country:
    #     return place_entity.countries
    #
    # if state:
    #     return place_entity.regions
    #
    # if city:
    #     return place_entity.cities
