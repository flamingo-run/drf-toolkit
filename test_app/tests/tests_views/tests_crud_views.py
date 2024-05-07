from datetime import timedelta
from unittest.mock import ANY

from rest_framework import status

from drf_kit.serializers import as_dict
from drf_kit.tests import BaseApiTest
from test_app import models
from test_app.tests.factories.beast_factories import BeastFactory
from test_app.tests.factories.training_pitch_factories import ReservationFactory, TrainingPitchFactory
from test_app.tests.tests_base import HogwartsTestMixin


class TestCRUDView(HogwartsTestMixin, BaseApiTest):
    url = "/houses"

    def setUp(self):
        super().setUp()
        self._set_up_houses()

    def test_list_endpoint(self):
        url = self.url

        response = self.client.get(url)

        # sorted by name ASC
        expected = [
            self.expected_houses[0],
            self.expected_houses[3],
            self.expected_houses[2],
            self.expected_houses[1],
        ]
        self.assertResponseList(expected, response)

    def test_detail_endpoint(self):
        house = self.houses[0]
        url = f"{self.url}/{house.pk}"

        response = self.client.get(url)

        expected = self.expected_houses[0]
        self.assertResponseDetail(expected, response)

    def test_post_endpoint(self):
        url = self.url
        data = {
            "name": "#Always",
            "points_boost": 3.1,
        }
        response = self.client.post(url, data=data)

        expected = {
            "id": ANY,
            "name": "#Always",
            "points_boost": "3.10",
            "created_at": ANY,
        }
        self.assertResponseCreate(expected, response)

        houses = models.House.objects.all()
        self.assertEqual(5, houses.count())

    def test_patch_endpoint(self):
        house = self.houses[0]
        url = f"{self.url}/{house.pk}"
        data = {
            "points_boost": 3.14,
        }
        response = self.client.patch(url, data=data)

        expected_house = self.expected_houses[0]
        expected_house["points_boost"] = "3.14"

        self.assertResponseUpdated(expected_item=expected_house, response=response)

        houses = models.House.objects.all()
        self.assertEqual(4, houses.count())

    def test_put_endpoint(self):
        house = self.houses[0]
        url = f"{self.url}/{house.pk}"
        data = {
            "name": "Not Griffindor",
        }
        response = self.client.put(url, data=data)
        self.assertResponseNotAllowed(response=response)

    def test_not_found_endpoint(self):
        url = f"{self.url}/1234123"
        response = self.client.get(url)
        self.assertResponseNotFound(response=response)

    def test_delete_endpoint(self):
        house = self.houses[0]
        url = f"{self.url}/{house.pk}"
        response = self.client.delete(url)

        self.assertResponseDeleted(response=response)

        houses = models.House.objects.all()
        self.assertEqual(3, houses.count())


class TestConstraintView(HogwartsTestMixin, BaseApiTest):
    url = "/beasts"

    def test_post_endpoint_with_existing(self):
        beast = BeastFactory()

        url = self.url
        data = {
            "name": beast.name,
            "age": beast.age,
        }

        response = self.client.post(url, data=data)

        self.assertEqual(409, response.status_code)
        expected = {"errors": f"A Beast with `name={beast.name} and age={beast.age}` already exists."}
        self.assertResponse(expected_status=status.HTTP_409_CONFLICT, expected_body=expected, response=response)

        beasts = models.Beast.objects.all()
        self.assertEqual(1, beasts.count())

    def test_patch_endpoint_with_existing(self):
        existing_beast, beast = BeastFactory.create_batch(2)

        url = f"{self.url}/{beast.pk}"
        data = {
            "name": existing_beast.name,
            "age": existing_beast.age,
        }

        response = self.client.patch(url, data=data)

        self.assertEqual(409, response.status_code)
        expected = {"errors": f"A Beast with `name={existing_beast.name} and age={existing_beast.age}` already exists."}
        self.assertResponse(expected_status=status.HTTP_409_CONFLICT, expected_body=expected, response=response)

        beasts = models.Beast.objects.all()
        self.assertEqual(2, beasts.count())

    def test_post_endpoint_with_constraint_error(self):
        url = self.url
        data = {
            "name": "Griffin",
            "age": -42,
        }

        response = self.client.post(url, data=data)

        expected = {
            "errors": "This Beast violates the check `minimum-beast-age` which states `(AND: ('age__gte', 0))`",
        }
        self.assertResponse(expected_status=status.HTTP_400_BAD_REQUEST, expected_body=expected, response=response)

        beasts = models.Beast.objects.all()
        self.assertEqual(0, beasts.count())


class TestExclusionConstraintView(HogwartsTestMixin, BaseApiTest):
    url = "/reservations"

    def test_post_endpoint_with_overlap_period(self):
        reservation = ReservationFactory()

        url = self.url
        data = {
            "wizard_id": reservation.wizard.pk,
            "pitch_id": reservation.pitch.pk,
            "period": as_dict(reservation.period),
        }
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(409, response.status_code)

        reservation = models.Reservation.objects.all()
        self.assertEqual(1, reservation.count())

    def test_patch_endpoint_with_overlap_period(self):
        pitch = TrainingPitchFactory(name="Quidditch")
        existing_reservation = ReservationFactory(pitch_id=pitch.pk)

        _, upper = existing_reservation.period
        later_period = (upper + timedelta(hours=1), upper + timedelta(hours=2))
        reservation = ReservationFactory(pitch_id=pitch.pk, period=later_period)

        url = f"{self.url}/{reservation.pk}"
        data = {"period": as_dict(existing_reservation.period)}
        response = self.client.patch(url, data=data, format="json")
        self.assertEqual(409, response.status_code)

        reservation = models.Reservation.objects.all()
        self.assertEqual(2, reservation.count())
