from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from .serializers import UploadSerializer, DatePickerSerializer, TextInputBoxSerializer
import pandas as pd
from django.core.files.storage import FileSystemStorage
import os
from API.models import *
from django.db import transaction
import numpy as np
from rest_framework import mixins
from rest_framework import generics
from .models import NewsTimeSeries
from .helpers import get_word_freq, get_human_names, get_sentiment, get_location
# from nltk.corpus import stopwords
# stop = stopwords.words('english')
from operator import and_, or_
from functools import reduce
from django.db.models import Q, Count
from django.shortcuts import HttpResponse
import plotly.express as px
from django.template import loader
from django.conf import settings
from django.shortcuts import render


def graphs(request):
    queryset = NewsTimeSeries.objects.all()

    queryset = queryset.values('date').annotate(count=Count('date')).order_by('date')
    # print(queryset[0])
    df = pd.DataFrame.from_dict(queryset)
    # print(df.tail())
    # df1 = df.groupby(df['date']).size().reset_index(name='count')
    # 'tableview/static/csv/20_Startups.csv' is the django
    # directory where csv file exist.
    # Manipulate DataFrame using to_html() function
    # s = df.style.set_table_styles([
    #     {'selector': 'th.col_heading', 'props': 'text-align: center;'},
    #     {'selector': 'th.col_heading.level0', 'props': 'font-size: 1.5em;'},
    # ], overwrite=False)
    # geeks_object = s.to_html()
    x = list(df["date"].tolist())
    y = list(df["count"].tolist())

    fig = px.line(x=x, y=y)

    root = os.path.join(settings.BASE_DIR, "templates", "index.html")
    fig.write_html(root)
    # a = fig.to_html()
    # print(a)
    # template = loader.get_template(root)
    context = {
        'latest_question_list': "text",
    }
    return render(request, 'index.html', context)


class UploadViewSet(ViewSet):
    serializer_class = UploadSerializer
    queryset = NewsTimeSeries.objects.all()

    def list(self, request):
        queryset = NewsTimeSeries.objects.all().values(
            "date",
            "author__name",
            "publication__name",
            "title",
            "content"
        )[:5]
        return Response(queryset)

    def create(self, request):
        # file_uploaded = request.FILES.get('file_uploaded')
        # print(request.FILES)
        request_file = request.FILES['file_uploaded'] if 'file_uploaded' in request.FILES else None
        if request_file:
            # save attached file

            # create a new instance of FileSystemStorage
            fs = FileSystemStorage()
            file = fs.save(request_file.name, request_file)
            # the fileurl variable now contains the url to the file. This can be used to serve the file when needed.
            file_path = fs.path(request_file.name)

            if "xlsx" in request_file.name:
                df = pd.read_excel(file_path)

            elif "csv" in request_file.name:
                df = pd.read_csv(file_path)

            else:
                return Response("File format not supported")

            fields = ["title", "content", "date"]

            if all([x in df.columns for x in fields]):
                with transaction.atomic():
                    c=0
                    df = df.fillna("None")
                    df = df.dropna(subset=["title"])
                    df = df.dropna(subset=["date"])

                    for row in df.to_dict(orient="records"):
                        author = row.get("author", None)
                        publication = row.get("publication", None)

                        if not author  == np.nan or author == "nan" or author == "" or author == None or author == "None":
                            author = author.lower().strip()
                        else:
                            author = None

                        if not publication  == np.nan or publication == "nan" or publication == "" or publication == None or publication == "None":
                            publication = publication.lower().strip()
                        else:
                            publication = None

                        title = row["title"].strip()
                        content = row["content"].strip()
                        date = str(row["date"]).strip()

                        if date[0].isnumeric():
                            if "/" in date:
                                date = date.replace("/", "-")

                            if " " in date:
                                date = date.replace(" ", "-")

                            if author is None:
                                author_ins = None
                            else:
                                author_ins, created = Author.objects.get_or_create(name=author)

                            if publication is None:
                                publication_ins = None
                            else:
                                publication_ins, created = Publication.objects.get_or_create(name=publication)

                            ts = NewsTimeSeries.objects.create(
                                author=author_ins,
                                publication=publication_ins,
                                title = title,
                                content=content,
                                date=date
                            )
                            c=c+1

                return Response(f"Total : {len(df)}, uploaded : {c}")
            else:
                return Response(f"Columns not exist")
        else:
            return Response(f"file not uploaded")


class WordFrequencySet(ViewSet):
    serializer_class = DatePickerSerializer

    def list(self, request):
        queryset = NewsTimeSeries.objects.all().order_by("-date")
        start_date = queryset.last().date
        end_date = queryset.first().date
        queryset = {
            "USE CASE": "Which word's is getting appeared in most of the news's in given period",
            "TIP": "Choose dates to get results between that period",
            "AVAILABLE DATE": f"{start_date} to {end_date}"

        }
        return Response(queryset)

    def post(self, requests):
        # import nltk
        # nltk.download('stopwords')
        # from nltk.corpus import stopwords
        # STOPWORDS = set(stopwords.words('english'))
        # print(STOPWORDS)
        start_date = requests.data.get("start_date", None)
        end_date = requests.data.get("end_date", None)

        result = NewsTimeSeries.objects.all()

        if start_date:

            result = result.filter(
                date__gte = start_date,
            )

        if end_date:
            result = result.filter(
                date__lte= end_date
            )

        if result.exists():
            # print(result)
            if result.count() > 100:
                result = result[:100]

            result = result.values(
                "title",
                "content"
            )
            df = pd.DataFrame.from_dict(result)
            kwd = get_word_freq(df)
            # kwd = kwd[kwd["value"] > 1]
            result = kwd[:10].to_dict(orient="records")

        else:
            result = "No Data"

        return Response(result)


class NewsLookupSet(ViewSet):
    serializer_class = TextInputBoxSerializer

    def list(self, request):
        queryset = NewsTimeSeries.objects.all().order_by("-date")
        start_date = queryset.last().date
        end_date = queryset.first().date
        # print(start_date)

        queryset = {
            "USE CASE": "Search the particular word in news database for selected period & get sentiment along with it",
            "TIP": "Choose dates to get results between that period",
            "AVAILABLE DATE": f"{start_date} to {end_date}"
        }
        return Response(queryset)

    def post(self, requests):
        # import nltk
        # nltk.download('stopwords')
        # from nltk.corpus import stopwords
        # STOPWORDS = set(stopwords.words('english'))
        start_date = requests.data.get("start_date", None)
        end_date = requests.data.get("end_date", None)
        search = requests.data.get("search", None)
        sentiment = requests.data.get("fetch.sentiment", None)
        location = requests.data.get("fetch.location", None)
        mentioned = requests.data.get("fetch.mentioned", None)

        result = NewsTimeSeries.objects.all()

        if start_date:
            result = result.filter(
                date__gte=start_date,
            )

        if end_date:
            result = result.filter(
                date__lte=end_date
            )

        if search:
            result = result.filter(reduce(or_, [Q(title__icontains=search), Q(content__icontains=search)]))

        if result.exists():
            # print(result.count())

            if result.count() > 10:
                result = result[:10]
                # return Response("Facing Heavy Computation, Choose short period")

            result = result.values(
                "id",
                "title",
                "content",
                "date"
            )
            df = pd.DataFrame.from_dict(result)

            df["raw"] = df["title"] + "" + df["content"]
            # get_sentiment("House Republicans Fret About Winning Their Health Care Suit")

            if location:
                df['region'] = df['raw'].apply(
                    lambda x: get_location(x))

            if sentiment:
                df['sentiment'] = df['title'].apply(
                    lambda x: get_sentiment(x))

            if mentioned:
                df['mentioned'] = df['raw'].apply(
                    lambda x: list(set(get_human_names(x))))

            df = df.drop('raw', axis=1)

            result = df.to_dict(orient="records")

        else:
            result = "No Data"

        return Response(result)