from rest_framework import serializers

from .models import NewsTimeSeries


class UploadSerializer(serializers.Serializer):
    file_uploaded = serializers.FileField()
    class Meta:
        fields = ['file_uploaded']


class DatePickerSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    class Meta:
        fields = ['start_date', 'end_date']


class TextSerializer(serializers.Serializer):
    search = serializers.CharField()

    class Meta:
        fields = ['search',]


class ChooseFeature(serializers.Serializer):
    location = serializers.BooleanField(default=False)
    mentioned = serializers.BooleanField(default=False)
    sentiment = serializers.BooleanField(default=False)

    class Meta:
        fields = ['location', 'mentioned', 'sentiment']


class TextInputBoxSerializer(serializers.Serializer):
    search = TextSerializer()
    date = DatePickerSerializer()
    fetch = ChooseFeature()

    class Meta:
        fields = ['search', "date"]


class NewsTimeSeriesSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    publication = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = NewsTimeSeries
        fields = ["date", "author", "publication", "title", "content"]

