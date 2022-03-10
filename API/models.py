from django.db import models
from django.conf import settings
# Create your models here.


class Author(models.Model):
    name = models.CharField(max_length=160, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Authors"

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.lower()
        return super(Author, self).save(*args, **kwargs)


class Publication(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Publications"

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.lower()
        return super(Publication, self).save(*args, **kwargs)


class Country(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Countries"

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.lower()
        return super(Country, self).save(*args, **kwargs)


class State(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "States"

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.lower()
        return super(State, self).save(*args, **kwargs)


class City(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Cities"

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.lower()
        return super(City, self).save(*args, **kwargs)


class Mentioned(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Mentioned"

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.lower()
        return super(Mentioned, self).save(*args, **kwargs)


class NewsTimeSeries(models.Model):
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)
    publication = models.ForeignKey(Publication, on_delete=models.SET_NULL, null=True)

    Country = models.ManyToManyField(Country)
    State = models.ManyToManyField(State)
    City = models.ManyToManyField(City)
    Mentioned = models.ManyToManyField(Mentioned)

    title = models.TextField()
    content = models.TextField()
    date = models.DateField()

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name_plural = "NewsTimeSeries"
