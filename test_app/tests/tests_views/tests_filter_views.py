from rest_framework import status

from drf_kit.tests import BaseApiTest
from test_app.tests.factories.spell_cast_factories import CombatSpellCastFactory
from test_app.tests.factories.spell_factories import SpellFactory
from test_app.tests.factories.teacher_factories import TeacherFactory
from test_app.tests.factories.training_pitch_factories import TrainingPitchFactory
from test_app.tests.factories.wizard_factories import WizardFactory
from test_app.tests.tests_base import HogwartsTestMixin


class TestFilterView(HogwartsTestMixin, BaseApiTest):
    url = "/teachers"

    def test_filter_querystring(self):
        teachers = TeacherFactory.create_batch(5, name="Harry", is_ghost=False)
        TeacherFactory.create_batch(10, name="NotHarry")

        url = f"{self.url}?name=Harry"
        response = self.client.get(url)
        self.assertResponseItems(expected_items=teachers, response=response)

    def test_search_body(self):
        teacher = TeacherFactory(is_half_blood=True, is_ghost=False)
        TeacherFactory.create_batch(10, is_half_blood=True, is_ghost=False)
        TeacherFactory.create_batch(10, is_half_blood=False, is_ghost=False)

        url = f"{self.url}/search"
        search = {"is_half_blood": True, "id": teacher.id}
        response = self.client.post(url, data=search)
        self.assertResponseItems(expected_items=[teacher], response=response)

    def test_search_body_with_array(self):
        teachers = TeacherFactory.create_batch(10, is_ghost=False)
        TeacherFactory.create_batch(10, is_ghost=False)

        url = f"{self.url}/search"
        search = {"id": [t.id for t in teachers]}
        response = self.client.post(url, data=search)
        self.assertResponseItems(expected_items=teachers, response=response)

    def test_search_body_empty(self):
        teachers = TeacherFactory.create_batch(10, is_half_blood=True, is_ghost=False)

        url = f"{self.url}/search"
        search = {}
        response = self.client.post(url, data=search)
        self.assertResponseItems(expected_items=teachers, response=response)

    def test_search_body_malformed(self):
        TeacherFactory.create_batch(10, is_half_blood=True, is_ghost=False)

        url = f"{self.url}/search"
        search = "potato"
        response = self.client.post(url, data=search, content_type="application/text")
        self.assertEqual(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, response.status_code)

    def test_search_body_ordered(self):
        teachers = []
        for i in range(10, 20):
            teachers.append(TeacherFactory(id=i, is_ghost=False, picture=None))
        expected_teachers = [self.expected_teacher(teacher) for teacher in teachers]

        for i in range(200, 210):
            TeacherFactory(id=i, is_ghost=True, picture=None)  # noise

        url = f"{self.url}/search?sort=id"
        search = {"is_ghost": False}
        response = self.client.post(url, data=search)

        self.assertResponseList(expected_items=expected_teachers, response=response)

    def test_search_miss_with_different_body(self):
        url = f"{self.url}/search?name=Hermione"
        data = {"age": 20, "is_half_blood": False}

        response_json_miss = self.client.post(url, data=data)
        self.assertEqual(status.HTTP_200_OK, response_json_miss.status_code)
        self.assertEqual("MISS", response_json_miss["X-Cache"])

        data = {"age": 25, "is_half_blood": True}

        response_json_miss = self.client.post(url, data=data)
        self.assertEqual(status.HTTP_200_OK, response_json_miss.status_code)
        self.assertEqual("MISS", response_json_miss["X-Cache"])

    def test_search_hit_with_same_body(self):
        url = f"{self.url}/search?name=Hermione"
        data = {"age": 20, "is_half_blood": False}

        response_json_miss = self.client.post(url, data=data)
        self.assertEqual(status.HTTP_200_OK, response_json_miss.status_code)
        self.assertEqual("MISS", response_json_miss["X-Cache"])

        response_json_hit = self.client.post(url, data=data)
        self.assertEqual(status.HTTP_200_OK, response_json_hit.status_code)
        self.assertEqual("HIT", response_json_hit["X-Cache"])


class TestAnyOfFilter(BaseApiTest):
    def test_with_initial_value(self):
        pitch = TrainingPitchFactory(name="Poppins")
        TrainingPitchFactory(name="Big House")

        url = "/training-pitches"
        response = self.client.get(url)
        expected_ids = [pitch.pk]
        result_ids = [r["id"] for r in response.json()["results"]]
        self.assertEqual(expected_ids, result_ids)


class TestAllOfFilterView(HogwartsTestMixin, BaseApiTest):
    url = "/wizards-custom-filter"

    def setUp(self):
        super().setUp()

        self.spell_a = SpellFactory()
        self.spell_b = SpellFactory()

        self.wizard_a = WizardFactory()
        self.wizard_b = WizardFactory()

        CombatSpellCastFactory(wizard=self.wizard_a, spell=self.spell_a)
        CombatSpellCastFactory(wizard=self.wizard_a, spell=self.spell_b)

        CombatSpellCastFactory(wizard=self.wizard_b, spell=self.spell_a)

        self.wizard_noise = WizardFactory()
        self.spell_noise = SpellFactory()
        CombatSpellCastFactory(wizard=self.wizard_noise, spell=self.spell_noise)

    def test_filter_querystring(self):
        response = self.client.get(self.url, data={"spell_name": self.spell_a.name})
        self.assertResponseItems(expected_items=[self.wizard_a, self.wizard_b], response=response)

    def test_filter_multiple_spell_name_conjoined_return_wizards(self):
        response = self.client.get(self.url, data={"spell_name": [self.spell_a.name, self.spell_b.name]})
        self.assertResponseItems(expected_items=[self.wizard_a], response=response)

    def test_filter_multiple_spell_name_any_of_through_relationship(self):
        response = self.client.get(self.url, data={"any_spell_name": [self.spell_a.name, self.spell_b.name]})
        self.assertResponseItems(expected_items=[self.wizard_a, self.wizard_b], response=response)

    def test_filter_multiple_spell_name_disjointed_not_return_wizards(self):
        response = self.client.get(self.url, data={"spell_name": [self.spell_a.name, self.spell_noise.name]})
        self.assertResponseItems(expected_items=[], response=response)

    def test_filter_empty_spell_name_return_all_wizards(self):
        response = self.client.get(self.url, data={"spell_name": []})
        self.assertResponseItems(expected_items=[self.wizard_a, self.wizard_b, self.wizard_noise], response=response)

    def test_filter_wrong_spell_name_value_not_return_wizards(self):
        response = self.client.get(self.url, data={"spell_name": ["mandragora"]})
        self.assertResponseItems(expected_items=[], response=response)
