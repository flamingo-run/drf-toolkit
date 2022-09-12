import factory

from test_app.models import ExclusiveNews, News
from test_app.tests.factories.newsaper_factories import NewspaperFactory


class NewsFactory(factory.django.DjangoModelFactory):
    newspaper = factory.SubFactory(NewspaperFactory)

    class Meta:
        model = News


class ExclusiveNewsFactory(factory.django.DjangoModelFactory):
    newspaper = factory.SubFactory(NewspaperFactory)

    class Meta:
        model = ExclusiveNews
