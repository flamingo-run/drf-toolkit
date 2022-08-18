from test_app.tests.factories.newsaper_factories import NewspaperFactory
from test_app.tests.tests_models.tests_availability_models import TestAvailabilityModel


class TestSoftDeleteAvailabilityModel(TestAvailabilityModel):
    factory_class = NewspaperFactory

    def setUp(self):
        super().setUp()

        self.deleted = [
            self.factory_class(starts_at=self.very_past_date, ends_at=self.very_future_date),
            self.factory_class(starts_at=self.very_past_date, ends_at=self.past_date),
            self.factory_class(starts_at=None, ends_at=self.past_date),
            self.factory_class(starts_at=None, ends_at=self.future_date),
            self.factory_class(starts_at=None, ends_at=None),
            self.factory_class(starts_at=self.past_date, ends_at=self.future_date),
        ]
        for obj in self.deleted:
            obj.delete()

    def test_query_all(self):
        qs = self.model_class.objects.all_with_deleted()

        expected = self.past + self.current + self.future + self.deleted
        self.assertObjects(qs=qs, expected=expected)
