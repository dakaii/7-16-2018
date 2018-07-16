from django.db import models
from django.core.validators import RegexValidator


class Publisher(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)


class Category(models.Model):
    category_tag = models.CharField(max_length=255)

    def __unicode__(self):
        return self.category_tag


class Book(models.Model):
    isbn_number = models.CharField(max_length=13, validators=[RegexValidator(r'^[0-9]*$')])
    title = models.CharField(max_length=255)
    authors = models.ManyToManyField(Author)
    description = models.TextField(null=True)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, null=True)
    publication_date = models.DateField(null=True)
    categories = models.ManyToManyField(Category)
    thumbnail = models.URLField(null=True)

    def __unicode__(self):
        return self.title
