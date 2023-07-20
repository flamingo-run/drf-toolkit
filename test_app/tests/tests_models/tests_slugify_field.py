from drf_kit.tests import BaseApiTest
from test_app.tests.factories.article_factories import ExclusiveArticleFactory


class TestSlugifyField(BaseApiTest):
    def test_auto_slugify(self):
        article = ExclusiveArticleFactory(slug="Hello World")
        article.refresh_from_db()
        self.assertEqual(article.slug, "hello-world")

    def test_auto_slugify_unicode(self):
        article = ExclusiveArticleFactory(slug="]Helló Wôrld!")
        article.refresh_from_db()
        self.assertEqual(article.slug, "hello-world")
