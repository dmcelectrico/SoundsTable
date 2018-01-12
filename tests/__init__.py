import unittest
from persistence import *


class PersistenceTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = Database(provider='sqlite')

    def test_populate(self):
        self.db.add_sound(1, 'filenameA', 'text A', 'tags A')
        self.db.add_sound(2, 'filenameB', 'text B', 'tags B')
        self.db.add_sound(3, 'filenameC', 'text C', 'tags C')
        self.db.add_sound(4, 'filenamed', 'text D', 'tags D')
        self.assertEqual(len(self.db.get_sounds()), 4)

    def test_retrieve(self):
        self.assertIsNotNone(self.db.get_sound(filename='filenameA'))
        self.assertIsNotNone(self.db.get_sound(id=2))
        self.assertIsNotNone(self.db.get_sound(id=3, filename='filenameC'))
        self.assertIsNone(self.db.get_sound(id=4, filename='filenameB'))

    def test_remove(self):
        sound = self.db.get_sound(id=2)
        self.db.delete_sound(sound)
        self.assertEqual(len(self.db.get_sounds()), 3)


if __name__ == '__main__':
    unittest.main()