#!/usr/bin/env python3
"""Tests of inventory.py's names for the constants, and of the check that
counts an id given to more than one thing in the code.

    python3 -m unittest discover -s scripts -p 'test_*.py'

The repositories are stood in for: nothing is read from git.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import capabilities  # noqa: E402
import inventory  # noqa: E402


class FakeRepo:
    """a repository of these files, path to text"""

    def __init__(self, name, files):
        self.name = name
        self._files = files
        self.files = list(files)

    def code(self, *exts):
        return [f for f in self.files if f.endswith(exts)]

    def text(self, path):
        return self._files[path]


def constants_of(repo):
    inventory.rows.clear()
    inventory.clashes.clear()
    inventory.constants(repo)
    return {r['id']: (r['value'], r['where']) for r in inventory.rows.values()}


class ConstantNames(unittest.TestCase):
    def test_files_of_one_name_in_two_packages_are_named_by_their_directory(self):
        got = constants_of(FakeRepo('catalog', {
            'internal/chapters/backfill.go': 'package chapters\n\nconst (\n\tDefaultRate = 120\n\tDefaultRecords = 3600\n)\n',
            'internal/captions/backfill.go': 'package captions\n\nconst (\n\tDefaultRate = 600\n)\n',
            'internal/rest/limits.go': 'package rest\n\nconst MaxBody = 1 << 20\nconst PageSize = 50\n',
        }))
        self.assertEqual(got['constant:catalog:chapters/backfill.DefaultRate'], ('120', 'internal/chapters/backfill.go:4'))
        self.assertEqual(got['constant:catalog:captions/backfill.DefaultRate'], ('600', 'internal/captions/backfill.go:4'))
        self.assertNotIn('constant:catalog:backfill.DefaultRate', got, 'the clashing short name names neither')
        self.assertIn('constant:catalog:backfill.DefaultRecords', got, 'a name only one of them holds keeps its short id')
        self.assertIn('constant:catalog:limits.PageSize', got, 'every other id stays as it is')
        self.assertEqual(inventory.clashes, [])

    def test_twins_of_one_file_in_one_package_keep_the_one_name(self):
        got = constants_of(FakeRepo('app', {
            'shared/src/androidMain/kotlin/app/player/PlayerScreen.android.kt': 'const val SAVE_EVERY_MS = 10_000\n',
            'shared/src/iosMain/kotlin/app/player/PlayerScreen.ios.kt': 'const val SAVE_EVERY_MS = 10_000\n',
        }))
        self.assertEqual(list(got), ['constant:app:PlayerScreen.SAVE_EVERY_MS'])
        self.assertEqual(inventory.clashes, [])

    def test_a_clash_that_is_left_is_written_and_counted(self):
        constants_of(FakeRepo('app', {
            'app/src/one/Limits.kt': 'object A {\n    const val MAX = 5\n}\nobject B {\n    const val MAX = 7\n}\n',
        }))
        self.assertEqual(len(inventory.clashes), 1)
        rows = list(inventory.rows.values()) + inventory.clashes
        self.assertEqual(capabilities.clashing(rows), ['constant:app:Limits.MAX'])

    def test_no_clash_where_every_id_is_one_rows(self):
        self.assertEqual(capabilities.clashing([{'id': 'a'}, {'id': 'b'}]), [])


if __name__ == '__main__':
    unittest.main()
