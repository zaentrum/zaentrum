#!/usr/bin/env python3
"""Tests of release.py's check of where an image or a file comes from (T.C4).

    python3 -m unittest discover -s scripts -p 'test_*.py'

The registry, cosign and gh are stood in for: nothing leaves this machine.
"""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import release  # noqa: E402

PROV = "https://slsa.dev/provenance/v1"
SBOM = "https://spdx.dev/Document/v2.3"


def platform(digest, arch):
    return {"digest": digest, "platform": {"os": "linux", "architecture": arch}}


def attestation(digest, of):
    return {"digest": digest, "platform": {"os": "unknown", "architecture": "unknown"},
            "annotations": {"vnd.docker.reference.type": "attestation-manifest",
                            "vnd.docker.reference.digest": of}}


def layers(*kinds):
    return {"layers": [{"annotations": {"in-toto.io/predicate-type": k}} for k in kinds]}


class Registry:
    """ghcr.io as release.py asks it: a token, then manifests by tag or digest."""

    def __init__(self, manifests):
        self.manifests = manifests

    def urlopen(self, url, timeout=0):
        return contextlib.closing(io.BytesIO(json.dumps({"token": "t"}).encode()))

    def manifest(self, image, ref, token):
        return self.manifests[ref]


def done(code):
    return subprocess.CompletedProcess([], code, "", "")


class TestTC4WhereAnImageComesFrom(unittest.TestCase):

    def origin(self, manifests, cosign_code=0, version="v0.6.0"):
        reg = Registry(manifests)
        calls = []

        def run(cmd, cwd=None, check=True):
            calls.append(cmd)
            return done(cosign_code)
        with mock.patch.object(release.urllib.request, "urlopen", reg.urlopen), \
                mock.patch.object(release, "registry_manifest", reg.manifest), \
                mock.patch.object(release, "run", run):
            return release.image_origin("chino-api", "chino-api", "v0.6.0", version), calls

    def test_an_image_without_attestations(self):
        """T.C4: an image built with no record and no list lacks both, and its signature"""
        problems, _ = self.origin({"v0.6.0": {"manifests": [platform("sha256:a", "amd64")]}}, cosign_code=1)
        self.assertEqual(problems, [
            "ghcr.io/zaentrum/chino-api:v0.6.0 (linux/amd64) carries no record of its build",
            "ghcr.io/zaentrum/chino-api:v0.6.0 (linux/amd64) carries no list of the packages it holds",
            "ghcr.io/zaentrum/chino-api:v0.6.0 is not signed by a workflow of zaentrum/chino-api on v0.6.0",
        ])

    def test_an_image_with_its_record_its_list_and_its_signature(self):
        """T.C4: a signed image with both attached lacks nothing"""
        problems, _ = self.origin({
            "v0.6.0": {"manifests": [platform("sha256:a", "amd64"), attestation("sha256:b", "sha256:a")]},
            "sha256:b": layers(PROV, SBOM),
        })
        self.assertEqual(problems, [])

    def test_the_minimal_record_alone(self):
        """T.C4: the record without the list is not enough"""
        problems, _ = self.origin({
            "v0.6.0": {"manifests": [platform("sha256:a", "amd64"), attestation("sha256:b", "sha256:a")]},
            "sha256:b": layers(PROV),
        })
        self.assertEqual(problems, ["ghcr.io/zaentrum/chino-api:v0.6.0 (linux/amd64) carries no list of the packages it holds"])

    def test_each_platform_carries_its_own(self):
        """T.C4: an image for two processors needs both for each"""
        problems, _ = self.origin({
            "v0.6.0": {"manifests": [platform("sha256:a", "amd64"), platform("sha256:c", "arm64"),
                                     attestation("sha256:b", "sha256:a")]},
            "sha256:b": layers(PROV, SBOM),
        })
        self.assertEqual(problems, [
            "ghcr.io/zaentrum/chino-api:v0.6.0 (linux/arm64) carries no record of its build",
            "ghcr.io/zaentrum/chino-api:v0.6.0 (linux/arm64) carries no list of the packages it holds",
        ])

    def test_one_manifest_and_no_index(self):
        """T.C4: an image that is one manifest, as provenance: false builds it, lacks both"""
        problems, _ = self.origin({"v0.6.0": {"layers": []}})
        self.assertEqual(problems, [
            "ghcr.io/zaentrum/chino-api:v0.6.0 carries no record of its build",
            "ghcr.io/zaentrum/chino-api:v0.6.0 carries no list of the packages it holds",
        ])

    def test_the_signature_is_the_repositorys_workflow_on_the_tag(self):
        """T.C4: cosign is asked for a signature by a workflow of that repository, on the release's tag"""
        _, calls = self.origin({"v0.6.0": {"layers": []}}, version="v0.6.0-rc.1")
        cmd = calls[-1]
        self.assertEqual(cmd[:3], ["cosign", "verify", "ghcr.io/zaentrum/chino-api:v0.6.0"])
        self.assertEqual(cmd[cmd.index("--certificate-oidc-issuer") + 1], "https://token.actions.githubusercontent.com")
        self.assertEqual(cmd[cmd.index("--certificate-identity-regexp") + 1],
                         r"^https://github\.com/zaentrum/chino-api/\.github/workflows/[^@]+@refs/tags/v0\.6\.0-rc\.1$")


class TestTC4WhereAFileComesFrom(unittest.TestCase):

    def origin(self, name, record=0, sbom=0):
        calls = []

        def run(cmd, cwd=None, check=True):
            calls.append(cmd)
            if cmd[:3] == ["gh", "release", "download"]:
                return done(0)
            return done(sbom if "--predicate-type" in cmd else record)
        with mock.patch.object(release, "run", run):
            return release.asset_origin("zae", name, "v0.6.0"), calls

    def test_an_archive_needs_its_record_and_its_list(self):
        """T.C4: an archive without a signed record and a list lacks both"""
        problems, calls = self.origin("zae_0.6.0_linux_amd64.tar.gz", record=1, sbom=1)
        self.assertEqual(problems, [
            "zae's release v0.6.0: zae_0.6.0_linux_amd64.tar.gz has no record of its build signed by its workflow",
            "zae's release v0.6.0: zae_0.6.0_linux_amd64.tar.gz has no list of the packages it holds",
        ])
        self.assertIn(["--repo", "zaentrum/zae"], [c[-2:] for c in calls])

    def test_an_archive_with_both(self):
        """T.C4: an archive with its signed record and its list lacks nothing"""
        problems, _ = self.origin("zae_0.6.0_windows_arm64.zip")
        self.assertEqual(problems, [])

    def test_a_file_that_holds_no_packages(self):
        """T.C4: a file that is no archive needs its record and no list"""
        problems, calls = self.origin("checksums.txt", sbom=1)
        self.assertEqual(problems, [])
        self.assertFalse(any("--predicate-type" in c for c in calls))


class TestTC4TheMachineThatChecks(unittest.TestCase):

    def test_without_cosign(self):
        """T.C4: a machine without cosign cannot check a release, and says so"""
        with mock.patch.object(release.shutil, "which", lambda name: None), \
                mock.patch.object(release, "run", lambda cmd, cwd=None, check=True: done(0)):
            problems = release.tool_problems()
        self.assertEqual(len(problems), 1)
        self.assertIn("cosign is not on the PATH", problems[0])

    def test_with_both(self):
        """T.C4: with cosign and gh's attestations, nothing is missing"""
        with mock.patch.object(release.shutil, "which", lambda name: "/usr/bin/" + name), \
                mock.patch.object(release, "run", lambda cmd, cwd=None, check=True: done(0)):
            self.assertEqual(release.tool_problems(), [])



class TestWhatTheNotesMustNotName(unittest.TestCase):
    """The notes' check: the public rule of words, and the patterns of a file
    of one's own, which this repository does not hold."""

    def setUp(self):
        self.addCleanup(release.OWN_NAMES.clear)
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)

    def names(self, text):
        path = os.path.join(self.dir.name, "names")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def test_the_rule_of_words_flags_a_product_and_no_longer_word(self):
        product = "pl" "ex"
        notes = f"- player: reads a {product} library\n- catalog: a complex query is faster\n"
        self.assertEqual([f"- player: reads a {product} library"], release.unneutral_lines(notes))

    def test_without_a_names_file_no_host_is_looked_for(self):
        self.assertEqual([], release.unneutral_lines("- docs: the database is at db.example.org\n"))

    def test_a_names_file_adds_its_patterns_without_case(self):
        release.OWN_NAMES[:] = release.own_names(self.names(
            "# what is ours\n\nhost\t[a-z0-9.-]*\\.example\\.org\nmachine\t\\bbox[0-9]{2}\\b\n"))
        notes = "- docs: the database is at DB.Example.org\n- fix: box07 restarts\n- fix: a boxed set plays\n"
        self.assertEqual(["- docs: the database is at DB.Example.org", "- fix: box07 restarts"],
                         release.unneutral_lines(notes))

    def test_a_names_file_that_reads_as_nothing_fails(self):
        for text, said in (("# only a comment\n\n", "holds no pattern"),
                           ("host db.example.org\n", "line 1"),
                           ("host\t(\n", "line 1"),
                           ("\tdb\n", "line 1")):
            with self.subTest(text=text):
                with self.assertRaises(release.Failure) as e:
                    release.own_names(self.names(text))
                self.assertIn(said, str(e.exception))
        with self.assertRaises(release.Failure) as e:
            release.own_names(os.path.join(self.dir.name, "missing"))
        self.assertIn("cannot be read", str(e.exception))

    def test_a_names_file_that_cannot_be_read_stops_the_run_before_anything(self):
        err = io.StringIO()
        with mock.patch.object(release, "run", side_effect=AssertionError("nothing may run")), \
                contextlib.redirect_stderr(err):
            code = release.main(["finish", "v9.9.9", "--names-file", os.path.join(self.dir.name, "missing")])
        self.assertEqual(1, code)
        self.assertIn("cannot be read", err.getvalue())

    def test_the_names_file_comes_from_the_environment_too(self):
        path = self.names("host\tdb\\.example\\.org\n")
        seen = []
        with mock.patch.dict(os.environ, {"RELEASE_NAMES_FILE": path}), \
                mock.patch.object(release, "run"), \
                mock.patch.object(release, "cmd_check", side_effect=lambda args: seen.append(len(release.OWN_NAMES)) or 0):
            self.assertEqual(0, release.main(["check", "v9.9.9"]))
        self.assertEqual([1], seen)


if __name__ == "__main__":
    unittest.main()
