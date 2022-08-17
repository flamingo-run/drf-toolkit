from drf_kit.tests import BaseApiTest
from test_app.models import CombatSpell, EnvironmentalSpell, Spell
from test_app.tests.factories.spell_factories import CombatSpellFactory, EnvironmentalSpellFactory, SpellFactory


class TestMultiModel(BaseApiTest):
    def test_create_parent_model(self):
        spell = SpellFactory(name="Leviosa")
        self.assertEqual("spell", spell.type)

        self.assertFalse(EnvironmentalSpell.objects.exists())
        self.assertFalse(CombatSpell.objects.exists())

    def test_create_child_model(self):
        e_spell = EnvironmentalSpellFactory(name="Leviosa")
        self.assertEqual("environmentalspell", e_spell.type)

        c_spell = CombatSpellFactory(name="Petrificus")
        self.assertEqual("combatspell", c_spell.type)

        spells = Spell.objects.all()
        self.assertEqual(2, spells.count())
