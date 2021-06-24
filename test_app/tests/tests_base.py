from unittest.mock import ANY

from test_app.models import Wizard, Teacher, House, Patronus, Spell, SpellCast, Memory, TriWizardPlacement, Wand


class HogwartsTestMixin:
    def _set_up_wizards(self):
        return [
            Wizard.objects.create(
                id=100,
                name="Harry Potter",
                age=13,
                is_half_blood=True,
            ),
            Wizard.objects.create(
                id=200,
                name="Hermione Granger",
                age=12,
                is_half_blood=True,
            ),
            Wizard.objects.create(
                id=300,
                name="Draco Malfoy",
                age=13,
                is_half_blood=False,
            ),
            Wizard.objects.create(
                id=400,
                name="Sirius Black",
                age=40,
                is_half_blood=False,
            ),
        ]

    @property
    def expected_wizards(self):
        return [
            {"name": "Harry Potter", "is_half_blood": True, "received_letter_at": None},
            {"name": "Hermione Granger", "is_half_blood": True, "received_letter_at": None},
            {"name": "Draco Malfoy", "is_half_blood": False, "received_letter_at": None},
            {"name": "Sirius Black", "is_half_blood": False, "received_letter_at": None},
        ]

    @property
    def expected_detailed_wizards(self):
        return [
            {
                "id": 100,
                "created_at": ANY,
                "updated_at": ANY,
                "name": "Harry Potter",
                "age": 13,
                "is_half_blood": True,
                "received_letter_at": None,
                "picture": None,
                "house": None,
            },
            {
                "id": 200,
                "created_at": ANY,
                "updated_at": ANY,
                "name": "Hermione Granger",
                "age": 12,
                "is_half_blood": True,
                "received_letter_at": None,
                "picture": None,
                "house": None,
            },
            {
                "id": 300,
                "created_at": ANY,
                "updated_at": ANY,
                "name": "Draco Malfoy",
                "age": 13,
                "is_half_blood": False,
                "received_letter_at": None,
                "picture": None,
                "house": None,
            },
            {
                "id": 400,
                "created_at": ANY,
                "updated_at": ANY,
                "name": "Sirius Black",
                "age": 40,
                "is_half_blood": False,
                "received_letter_at": None,
                "picture": None,
                "house": None,
            },
        ]

    def _set_up_teachers(self):
        return [
            Teacher.objects.create(
                id=1000,
                name="Albus Dumbledore",
                is_half_blood=False,
            ),
            Teacher.objects.create(
                id=2000,
                name="Severus Snape",
                is_half_blood=True,
            ),
            Teacher.objects.create(
                id=3000,
                name="Minerva McGonagall",
                is_half_blood=False,
            ),
            Teacher.objects.create(
                id=4000,
                name="Filius Flitwick",
                is_half_blood=False,
            ),
        ]

    @property
    def expected_teachers(self):
        return [
            {
                "id": 1000,
                "created_at": ANY,
                "updated_at": ANY,
                "name": "Albus Dumbledore",
                "age": None,
                "is_half_blood": False,
                "received_letter_at": None,
                "picture": None,
                "is_ghost": False,
                "house": None,
            },
            {
                "id": 2000,
                "created_at": ANY,
                "updated_at": ANY,
                "name": "Severus Snape",
                "age": None,
                "is_half_blood": True,
                "received_letter_at": None,
                "picture": None,
                "is_ghost": False,
                "house": None,
            },
            {
                "id": 3000,
                "created_at": ANY,
                "updated_at": ANY,
                "name": "Minerva McGonagall",
                "age": None,
                "is_half_blood": False,
                "received_letter_at": None,
                "picture": None,
                "is_ghost": False,
                "house": None,
            },
            {
                "id": 4000,
                "created_at": ANY,
                "updated_at": ANY,
                "name": "Filius Flitwick",
                "age": None,
                "is_half_blood": False,
                "received_letter_at": None,
                "picture": None,
                "is_ghost": False,
                "house": None,
            },
        ]

    def _set_up_houses(self):
        return [
            House.objects.create(
                id=100,
                name="Gryffindor",
                points_boost=2.0,
            ),
            House.objects.create(
                id=200,
                name="Slytherin",
            ),
            House.objects.create(
                id=300,
                name="Ravenclaw",
            ),
            House.objects.create(
                id=400,
                name="Hufflepuff",
            ),
        ]

    @property
    def expected_houses(self):
        return [
            {
                "id": 100,
                "name": "Gryffindor",
                "points_boost": "2.00",
                "created_at": ANY,
            },
            {
                "id": 200,
                "name": "Slytherin",
                "points_boost": "1.00",
                "created_at": ANY,
            },
            {
                "id": 300,
                "name": "Ravenclaw",
                "points_boost": "1.00",
                "created_at": ANY,
            },
            {
                "id": 400,
                "name": "Hufflepuff",
                "points_boost": "1.00",
                "created_at": ANY,
            },
        ]

    @property
    def expected_stats_houses(self):
        house_a, house_b, house_c, house_d = self.expected_houses
        house_a["wizard_count"] = 2
        house_b["wizard_count"] = 1
        house_c["wizard_count"] = 0
        house_d["wizard_count"] = 0
        return house_a, house_b, house_c, house_d

    def _set_up_wizard_houses(self, wizards, houses):
        wizard_a, wizard_b, wizard_c, _ = wizards
        house_a, house_b, _, _ = houses

        wizard_a.house = house_a
        wizard_a.save()

        wizard_b.house = house_a
        wizard_b.save()

        wizard_c.house = house_b
        wizard_c.save()

    def _set_up_patronus(self, wizards):
        wizard_a, wizard_b, _, wizard_d = wizards

        patronus_a = Patronus.objects.create(
            id=10,
            name="Stag",
            color="purple",
            wizard=wizard_a,
        )
        patronus_b = Patronus.objects.create(
            id=20,
            name="Otter",
            color="white",
            wizard=wizard_b,
        )
        patronus_c = None
        patronus_d = Patronus.objects.create(
            id=40,
            name="Dog",
            color="blue",
            wizard=wizard_d,
        )
        return patronus_a, patronus_b, patronus_c, patronus_d

    @property
    def expected_patronus(self):
        return [
            {
                "id": 10,
                "name": "Stag",
                "color": "purple",
                "wizard": self.expected_wizards[0],
            },
            {
                "id": 20,
                "name": "Otter",
                "color": "white",
                "wizard": self.expected_wizards[1],
            },
            None,
            {
                "id": 40,
                "name": "Dog",
                "color": "blue",
                "wizard": self.expected_wizards[3],
            },
        ]

    def _set_up_spells(self):
        spell_a = Spell.objects.create(
            id=100,
            name="Crucio",
        )
        spell_b = Spell.objects.create(
            id=200,
            name="Stupefy",
        )
        spell_c = Spell.objects.create(
            id=300,
            name="Imperio",
        )
        return spell_a, spell_b, spell_c

    @property
    def expected_spells(self):
        return [
            {
                "id": 100,
                "name": "Crucio",
                "type": "spell",
                "created_at": ANY,
                "updated_at": ANY,
            },
            {
                "id": 200,
                "name": "Stupefy",
                "type": "spell",
                "created_at": ANY,
                "updated_at": ANY,
            },
            {
                "id": 300,
                "name": "Imperio",
                "type": "spell",
                "created_at": ANY,
                "updated_at": ANY,
            },
        ]

    def _set_up_spell_casts(self, spells, wizards):
        spell_a, spell_b, spell_c = spells
        wizard_a, wizard_b, wizard_c, wizard_d = wizards

        spell_cast_a = SpellCast.objects.create(
            id=100,
            wizard=wizard_a,
            spell=spell_a,
            is_successful=False,
        )
        spell_cast_b = SpellCast.objects.create(
            id=200,
            wizard=wizard_b,
            spell=spell_a,
            is_successful=True,
        )
        spell_cast_c = SpellCast.objects.create(
            id=300,
            wizard=wizard_c,
            spell=spell_b,
            is_successful=True,
        )
        spell_cast_d = SpellCast.objects.create(
            id=400,
            wizard=wizard_d,
            spell=spell_c,
            is_successful=False,
        )
        return spell_cast_a, spell_cast_b, spell_cast_c, spell_cast_d

    @property
    def expected_spell_casts(self):
        return [
            {
                "id": 100,
                "wizard": self.expected_detailed_wizards[0],
                "spell": self.expected_spells[0],
                "is_successful": False,
            },
            {
                "id": 200,
                "wizard": self.expected_detailed_wizards[1],
                "spell": self.expected_spells[0],
                "is_successful": True,
            },
            {
                "id": 300,
                "wizard": self.expected_detailed_wizards[2],
                "spell": self.expected_spells[1],
                "is_successful": True,
            },
            {
                "id": 400,
                "wizard": self.expected_detailed_wizards[3],
                "spell": self.expected_spells[2],
                "is_successful": False,
            },
        ]

    def _set_up_memories(self, wizards):
        wizard_a, wizard_b, wizard_c, _ = wizards

        memory_a = Memory.objects.create(
            id=1000,
            owner=wizard_a,
            description="Stairs",
        )
        memory_b = Memory.objects.create(
            id=2000,
            owner=wizard_b,
            description="Leviosaaa",
        )
        memory_c = Memory.objects.create(
            id=3000,
            owner=wizard_c,
            description="Ew Harry",
        )

        return memory_a, memory_b, memory_c

    @property
    def expected_memories(self):
        return [
            {
                "id": 1000,
                "owner_id": 100,
                "description": "Stairs",
            },
            {
                "id": 2000,
                "owner_id": 200,
                "description": "Leviosaaa",
            },
            {
                "id": 3000,
                "owner_id": 300,
                "description": "Ew Harry",
            },
        ]

    def _set_up_placements(self, wizards):
        wizard_a, wizard_b, wizard_c, wizard_d = wizards

        placament_a1 = TriWizardPlacement.objects.create(
            id=1000,
            wizard=wizard_a,
            year=1950,
            prize="cake",
        )
        placament_a2 = TriWizardPlacement.objects.create(
            id=2000,
            wizard=wizard_b,
            year=1950,
            prize="pride",
        )
        placament_b1 = TriWizardPlacement.objects.create(
            id=3000,
            wizard=wizard_c,
            year=1960,
            prize="hug",
        )
        placament_b2 = TriWizardPlacement.objects.create(
            id=4000,
            wizard=wizard_d,
            year=1960,
            prize="points",
        )

        return placament_a1, placament_a2, placament_b1, placament_b2

    @property
    def expected_placements(self):
        return [
            {
                "id": 1000,
                "wizard_id": 100,
                "year": 1950,
            },
            {
                "id": 2000,
                "wizard_id": 200,
                "year": 1950,
            },
            {
                "id": 3000,
                "wizard_id": 300,
                "year": 1960,
            },
            {
                "id": 4000,
                "wizard_id": 400,
                "year": 1960,
            },
        ]

    def _set_up_wands(self):
        return [
            Wand.objects.create(
                id=10,
                name="Aspen",
            ),
            Wand.objects.create(
                id=20,
                name="Beech",
            ),
            Wand.objects.create(
                id=30,
                name="Cedar",
            ),
            Wand.objects.create(
                id=40,
                name="Elder",
            ),
            Wand.objects.create(
                id=50,
                name="Elm",
            ),
        ]

    @property
    def expected_wands(self):
        return [
            {"id": 10, "name": "Aspen"},
            {"id": 20, "name": "Beech"},
            {"id": 30, "name": "Cedar"},
            {"id": 40, "name": "Elder"},
            {"id": 50, "name": "Elm"},
        ]
