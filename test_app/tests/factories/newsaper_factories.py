import factory

from test_app.models import Newspaper


class NewspaperFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Newspaper
