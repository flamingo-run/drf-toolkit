import factory

from test_app.models import Article
from test_app.tests.factories.newsaper_factories import NewspaperFactory


class ArticleFactory(factory.django.DjangoModelFactory):
    newspaper = factory.SubFactory(NewspaperFactory)

    class Meta:
        model = Article
