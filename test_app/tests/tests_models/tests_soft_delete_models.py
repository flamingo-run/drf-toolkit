from drf_kit import exceptions
from drf_kit.tests import BaseApiTest
from test_app.models import (
    Article,
    BeastCategory,
    BeastOwnership,
    ExclusiveArticle,
    ExclusiveNews,
    Memory,
    News,
    Newspaper,
)
from test_app.tests.factories.article_factories import ArticleFactory, ExclusiveArticleFactory
from test_app.tests.factories.beast_category_factories import BeastCategoryFactory
from test_app.tests.factories.beast_factories import BeastFactory
from test_app.tests.factories.beast_owner_factories import BeastOwnerFactory
from test_app.tests.factories.beast_ownership_factories import BeastOwnershipFactory
from test_app.tests.factories.memory_factories import MemoryFactory
from test_app.tests.factories.news_factories import ExclusiveNewsFactory, NewsFactory
from test_app.tests.factories.newsaper_factories import NewspaperFactory
from test_app.tests.factories.wizard_factories import WizardFactory
from test_app.tests.tests_base import HogwartsTestMixin


class TestSoftDeleteModel(HogwartsTestMixin, BaseApiTest):
    def test_delete_model(self):
        memory = MemoryFactory()
        memory.description = "Any short description"
        self.assertIsNone(memory.deleted_at)

        memory.delete()
        memory.refresh_from_db()

        self.assertEqual(memory.description, "Any short description")
        self.assertIsNotNone(memory.deleted_at)

    def test_undelete_model(self):
        memory = MemoryFactory()
        memory.delete()
        memory.refresh_from_db()

        memory.description = "Any short description"
        memory.undelete()
        memory.refresh_from_db()
        self.assertEqual(memory.description, "Any short description")
        self.assertIsNone(memory.deleted_at)

    def test_hard_delete_model(self):
        memory = MemoryFactory()
        self.assertIsNone(memory.deleted_at)

        memory.delete()
        memory.refresh_from_db()
        self.assertIsNotNone(memory.deleted_at)

        memory.delete()
        with self.assertRaises(Memory.DoesNotExist):
            memory.refresh_from_db()

    def test_hard_with_queryset(self):
        memory = MemoryFactory()
        self.assertIsNone(memory.deleted_at)

        Memory.objects.all().hard_delete()

        with self.assertRaises(Memory.DoesNotExist):
            memory.refresh_from_db()

    def test_update_deleted_using_model(self):
        new_description = "Parents fighting Voldemort"
        memory = MemoryFactory()
        memory.delete()
        memory.refresh_from_db()

        memory.description = new_description

        with self.assertRaises(exceptions.UpdatingSoftDeletedException):
            memory.save()

        memory.refresh_from_db()
        self.assertNotEqual(new_description, memory.description)
        self.assertIsNotNone(memory.deleted_at)

    def test_update_deleted_using_queryset(self):
        new_description = "Parents fighting Voldemort"
        memory_a = MemoryFactory()
        memory_b = MemoryFactory()
        memory_b.delete()

        Memory.objects.all().update(description=new_description)

        memory_a.refresh_from_db()
        self.assertEqual(new_description, memory_a.description)

        memory_b.refresh_from_db()
        self.assertNotEqual(new_description, memory_b.description)

    def test_delete_using_model(self):
        memory = MemoryFactory()
        memory.delete()

        memory.refresh_from_db()
        self.assertIsNotNone(memory.deleted_at)

    def test_delete_using_queryset(self):
        memory_a = MemoryFactory()
        memory_b = MemoryFactory()

        Memory.objects.all().delete()

        memory_a.refresh_from_db()
        self.assertIsNotNone(memory_a.deleted_at)

        memory_b.refresh_from_db()
        self.assertIsNotNone(memory_b.deleted_at)

    def test_filter_by_default(self):
        memory_a = MemoryFactory()

        memory_b = MemoryFactory()
        memory_b.delete()

        memory_c = MemoryFactory()

        memories = Memory.objects.all()
        self.assertEqual(2, memories.count())

        [mem_c, mem_a] = memories
        self.assertEqual(memory_a, mem_a)
        self.assertEqual(memory_c, mem_c)

        deleted_memory = Memory.objects.get(pk=memory_b.pk)
        self.assertIsNotNone(deleted_memory.deleted_at)

    def test_filter_with_deleted(self):
        memory_a = MemoryFactory()

        memory_b = MemoryFactory()
        memory_b.delete()

        memory_c = MemoryFactory()

        memories = Memory.objects.all_with_deleted()
        self.assertEqual(3, memories.count())

        [mem_c, mem_b, mem_a] = memories
        self.assertEqual(memory_a, mem_a)
        self.assertEqual(memory_b, mem_b)
        self.assertEqual(memory_c, mem_c)

        deleted_memory = Memory.objects.get(pk=memory_b.pk)
        self.assertIsNotNone(deleted_memory.deleted_at)

    def test_get_referenced_deleted(self):
        wizard = WizardFactory()
        memory_a = MemoryFactory(owner=wizard)
        memory_b = MemoryFactory(owner=wizard)
        memory_b.delete()

        memories = wizard.memories.all()
        self.assertEqual(1, memories.count())
        self.assertEqual(memory_a, memories.first())

        memories = wizard.memories.all_with_deleted()
        self.assertEqual(2, memories.count())

    def test_get_m2m(self):
        owner = BeastOwnerFactory()
        ownership_a, ownership_b, ownership_c = BeastOwnershipFactory.create_batch(3, owner=owner)

        self.assertEqual(3, owner.beasts.count())
        ownership_b.delete()

        self.assertEqual(2, BeastOwnership.objects.count())
        self.assertEqual(3, owner.beasts.count())  # FIXME: it should be only 2 items

    def test_get_m2m_reverse(self):
        beast = BeastFactory()
        ownership_a, ownership_b, ownership_c = BeastOwnershipFactory.create_batch(3, beast=beast)

        self.assertEqual(3, beast.owners.count())
        ownership_b.delete()

        self.assertEqual(2, BeastOwnership.objects.count())
        self.assertEqual(3, beast.owners.count())  # FIXME: it should be only 2 items

    def test_get_m2o(self):
        category_a, category_b = BeastCategoryFactory.create_batch(2)
        BeastFactory.create_batch(2, category=category_a)
        beast_b1, beast_b2 = BeastFactory.create_batch(2, category=category_b)

        self.assertEqual(2, BeastCategory.objects.count())
        self.assertEqual(2, BeastCategory.objects.filter(beasts__age__gte=1).distinct().count())
        beast_b1.delete()
        beast_b2.delete()

        self.assertEqual(2, BeastCategory.objects.count())
        self.assertEqual(
            2,
            BeastCategory.objects.filter(beasts__age__gte=1).distinct().count(),
        )  # FIXME: it should be only 1 item


class TestSoftDeleteCascadeModel(HogwartsTestMixin, BaseApiTest):
    def test_delete_m2m_related(self):
        newspaper = NewspaperFactory()
        ArticleFactory.create_batch(5, newspaper=newspaper)
        ArticleFactory.create_batch(5)  # noise

        newspaper.delete()
        self.assertEqual(5, Article.objects.all().count())
        self.assertEqual(10, Article.objects.all_with_deleted().count())

    def test_delete_m2m_related_using_queryset(self):
        newspaper = NewspaperFactory()
        ArticleFactory.create_batch(5, newspaper=newspaper)
        ArticleFactory.create_batch(5)  # noise

        Newspaper.objects.filter(pk=newspaper.pk).delete()
        self.assertEqual(5, Article.objects.all().count())
        self.assertEqual(10, Article.objects.all_with_deleted().count())

    def test_delete_o2m_related(self):
        newspaper = NewspaperFactory()
        ExclusiveArticleFactory(newspaper=newspaper)
        ExclusiveArticleFactory.create_batch(5)  # noise

        newspaper.delete()
        self.assertEqual(5, ExclusiveArticle.objects.all().count())
        self.assertEqual(6, ExclusiveArticle.objects.all_with_deleted().count())

    def test_delete_o2m_related_using_queryset(self):
        newspaper = NewspaperFactory()
        ExclusiveArticleFactory(newspaper=newspaper)
        ExclusiveArticleFactory.create_batch(5)  # noise

        Newspaper.objects.filter(pk=newspaper.pk).delete()
        self.assertEqual(5, ExclusiveArticle.objects.all().count())
        self.assertEqual(6, ExclusiveArticle.objects.all_with_deleted().count())


class TestSoftDeleteSetNullModel(HogwartsTestMixin, BaseApiTest):
    def test_delete_m2m_related(self):
        newspaper = NewspaperFactory()
        NewsFactory.create_batch(5, newspaper=newspaper)
        NewsFactory.create_batch(5)  # noise

        newspaper.delete()
        self.assertEqual(10, News.objects.all().count())
        self.assertEqual(10, News.objects.all_with_deleted().count())
        self.assertEqual(5, News.objects.filter(newspaper__isnull=True).count())

    def test_delete_m2m_related_using_queryset(self):
        newspaper = NewspaperFactory()
        NewsFactory.create_batch(5, newspaper=newspaper)
        NewsFactory.create_batch(5)  # noise

        Newspaper.objects.filter(pk=newspaper.pk).delete()
        self.assertEqual(10, News.objects.all().count())
        self.assertEqual(10, News.objects.all_with_deleted().count())
        self.assertEqual(5, News.objects.filter(newspaper__isnull=True).count())

    def test_delete_o2m_related(self):
        newspaper = NewspaperFactory()
        ExclusiveNewsFactory(newspaper=newspaper)
        ExclusiveNewsFactory.create_batch(5)  # noise

        newspaper.delete()
        self.assertEqual(6, ExclusiveNews.objects.all().count())
        self.assertEqual(6, ExclusiveNews.objects.all_with_deleted().count())
        self.assertEqual(1, ExclusiveNews.objects.filter(newspaper__isnull=True).count())

    def test_delete_o2m_related_using_queryset(self):
        newspaper = NewspaperFactory()
        ExclusiveNewsFactory(newspaper=newspaper)
        ExclusiveNewsFactory.create_batch(5)  # noise

        Newspaper.objects.filter(pk=newspaper.pk).delete()
        self.assertEqual(6, ExclusiveNews.objects.all().count())
        self.assertEqual(6, ExclusiveNews.objects.all_with_deleted().count())
        self.assertEqual(1, ExclusiveNews.objects.filter(newspaper__isnull=True).count())
