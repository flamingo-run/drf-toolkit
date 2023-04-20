from unittest.mock import ANY

from drf_kit.serializers import as_str
from test_app import models
from test_app.tests.factories.house_factories import HouseFactory
from test_app.tests.factories.memory_factories import MemoryFactory
from test_app.tests.factories.patronus_factories import PatronusFactory
from test_app.tests.factories.spell_cast_factories import CombatSpellCastFactory
from test_app.tests.factories.spell_factories import SpellFactory
from test_app.tests.factories.teacher_factories import TeacherFactory
from test_app.tests.factories.tri_wizard_placement_factories import TriWizardPlacementFactory
from test_app.tests.factories.wand_factories import WandFactory
from test_app.tests.factories.wizard_factories import WizardFactory


class HogwartsTestMixin:
    @classmethod
    def expected_teacher(cls, teacher: models.Teacher) -> dict:
        return {
            "id": teacher.id,
            "created_at": ANY,
            "updated_at": ANY,
            "name": teacher.name,
            "age": teacher.age,
            "is_half_blood": teacher.is_half_blood,
            "received_letter_at": as_str(teacher.received_letter_at),
            "picture": teacher.picture.url if teacher.picture else None,
            "is_ghost": teacher.is_ghost,
            "house": None,
        }

    def _set_up_wizards(self):
        self.wizards = [
            WizardFactory(
                name="Harry Potter",
                age=13,
                is_half_blood=True,
                picture=None,
            ),
            WizardFactory(
                name="Hermione Granger",
                age=12,
                is_half_blood=True,
                picture=None,
            ),
            WizardFactory(
                name="Draco Malfoy",
                age=13,
                is_half_blood=False,
                picture=None,
            ),
            WizardFactory(
                name="Sirius Black",
                age=40,
                is_half_blood=False,
                picture=None,
            ),
        ]

    @property
    def expected_wizards(self):
        return [
            {
                "name": wizard.name,
                "is_half_blood": wizard.is_half_blood,
                "received_letter_at": as_str(wizard.received_letter_at),
            }
            for wizard in self.wizards
        ]

    @property
    def expected_detailed_wizards(self):
        return [
            {
                "id": wizard.id,
                "created_at": ANY,
                "updated_at": ANY,
                "name": wizard.name,
                "age": wizard.age,
                "is_half_blood": wizard.is_half_blood,
                "received_letter_at": as_str(wizard.received_letter_at),
                "picture": wizard.picture.url if wizard.picture else None,
                "house": None,
            }
            for wizard in self.wizards
        ]

    def _set_up_teachers(self):
        self.teachers = [
            TeacherFactory(
                name="Albus Dumbledore",
                is_half_blood=False,
                is_ghost=False,
                picture=None,
            ),
            TeacherFactory(
                name="Severus Snape",
                is_half_blood=True,
                is_ghost=False,
                picture=None,
            ),
            TeacherFactory(
                name="Minerva McGonagall",
                is_half_blood=False,
                is_ghost=False,
                picture=None,
            ),
            TeacherFactory(
                name="Filius Flitwick",
                is_half_blood=False,
                is_ghost=False,
                picture=None,
            ),
        ]

    @property
    def expected_teachers(self):
        return [self.expected_teacher(teacher) for teacher in self.teachers]

    def _set_up_houses(self):
        self.houses = [
            HouseFactory(
                name="Gryffindor",
                points_boost=2.0,
            ),
            HouseFactory(
                name="Slytherin",
            ),
            HouseFactory(
                name="Ravenclaw",
            ),
            HouseFactory(
                name="Hufflepuff",
            ),
        ]

    @property
    def expected_houses(self):
        return [
            {
                "id": house.id,
                "name": house.name,
                "points_boost": f"{house.points_boost:.2f}",
                "created_at": as_str(house.created_at),
            }
            for house in self.houses
        ]

    @property
    def expected_stats_houses(self):
        house_a, house_b, house_c, house_d = self.expected_houses
        house_a["wizard_count"] = 2
        house_b["wizard_count"] = 1
        house_c["wizard_count"] = 0
        house_d["wizard_count"] = 0
        return house_a, house_b, house_c, house_d

    def _set_up_wizard_houses(self):
        wizard_a, wizard_b, wizard_c, _ = self.wizards
        house_a, house_b, _, _ = self.houses

        wizard_a.house = house_a
        wizard_a.save()

        wizard_b.house = house_a
        wizard_b.save()

        wizard_c.house = house_b
        wizard_c.save()

    def _set_up_patronus(self):
        wizard_a, wizard_b, _, wizard_d = self.wizards

        self.patronus = [
            PatronusFactory(
                name="Stag",
                color="purple",
                wizard=wizard_a,
            ),
            PatronusFactory(
                name="Otter",
                color="white",
                wizard=wizard_b,
            ),
            None,
            PatronusFactory(
                name="Dog",
                color="blue",
                wizard=wizard_d,
            ),
        ]

    @property
    def expected_patronus(self):
        return [
            (
                {
                    "id": patronus.id,
                    "name": patronus.name,
                    "color": patronus.color,
                    "wizard": {
                        "name": patronus.wizard.name,
                        "is_half_blood": patronus.wizard.is_half_blood,
                        "received_letter_at": as_str(patronus.wizard.received_letter_at),
                    },
                }
                if patronus
                else None
            )
            for patronus in self.patronus
        ]

    def _set_up_spells(self):
        self.spells = [
            SpellFactory(
                name="Crucio",
            ),
            SpellFactory(
                name="Stupefy",
            ),
            SpellFactory(
                name="Imperio",
            ),
        ]

    @property
    def expected_spells(self):
        return [
            {
                "id": spell.id,
                "name": spell.name,
                "type": spell.type,
                "created_at": ANY,
                "updated_at": ANY,
            }
            for spell in self.spells
        ]

    def _set_up_spell_casts(self):
        spell_a, spell_b, spell_c = self.spells
        wizard_a, wizard_b, wizard_c, wizard_d = self.wizards

        self.spell_casts = [
            CombatSpellCastFactory(
                wizard=wizard_a,
                spell=spell_a,
                is_successful=False,
            ),
            CombatSpellCastFactory(
                wizard=wizard_b,
                spell=spell_a,
                is_successful=True,
            ),
            CombatSpellCastFactory(
                wizard=wizard_c,
                spell=spell_b,
                is_successful=True,
            ),
            CombatSpellCastFactory(
                wizard=wizard_d,
                spell=spell_c,
                is_successful=False,
            ),
        ]

    @property
    def expected_spell_casts(self):
        return [
            {
                "id": spell_cast.id,
                "wizard": {
                    "id": spell_cast.wizard.id,
                    "created_at": ANY,
                    "updated_at": ANY,
                    "name": spell_cast.wizard.name,
                    "age": spell_cast.wizard.age,
                    "is_half_blood": spell_cast.wizard.is_half_blood,
                    "received_letter_at": as_str(spell_cast.wizard.received_letter_at),
                    "picture": spell_cast.wizard.picture.url if spell_cast.wizard.picture else None,
                    "house": None,
                },
                "spell": {
                    "id": spell_cast.spell.id,
                    "name": spell_cast.spell.name,
                    "type": spell_cast.spell.type,
                    "created_at": ANY,
                    "updated_at": ANY,
                },
                "is_successful": spell_cast.is_successful,
            }
            for spell_cast in self.spell_casts
        ]

    def _set_up_memories(self):
        wizard_a, wizard_b, wizard_c, _ = self.wizards

        self.memories = [
            MemoryFactory(
                owner=wizard_a,
                description="Stairs",
            ),
            MemoryFactory(
                owner=wizard_b,
                description="Leviosaaa",
            ),
            MemoryFactory(
                owner=wizard_c,
                description="Ew Harry",
            ),
        ]

    @property
    def expected_memories(self):
        return [
            {
                "id": memory.id,
                "owner_id": memory.owner_id,
                "description": memory.description,
            }
            for memory in self.memories
        ]

    def _set_up_placements(self):
        wizard_a, wizard_b, wizard_c, wizard_d = self.wizards

        self.placements = [
            TriWizardPlacementFactory(
                wizard=wizard_a,
                year=1950,
                prize="cake",
            ),
            TriWizardPlacementFactory(
                wizard=wizard_b,
                year=1950,
                prize="pride",
            ),
            TriWizardPlacementFactory(
                wizard=wizard_c,
                year=1960,
                prize="hug",
            ),
            TriWizardPlacementFactory(
                wizard=wizard_d,
                year=1960,
                prize="points",
            ),
        ]

    @property
    def expected_placements(self):
        return [
            {
                "id": placement.id,
                "wizard_id": placement.wizard_id,
                "year": placement.year,
            }
            for placement in self.placements
        ]

    def _set_up_wands(self):
        self.wands = [
            WandFactory(
                name="Aspen",
            ),
            WandFactory(
                name="Beech",
            ),
            WandFactory(
                name="Cedar",
            ),
            WandFactory(
                name="Elder",
            ),
            WandFactory(
                name="Elm",
            ),
        ]

    @property
    def expected_wands(self):
        return [{"id": wand.id, "name": wand.name} for wand in self.wands]
