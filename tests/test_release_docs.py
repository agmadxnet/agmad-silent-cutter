"""Regression tests for clean future packages and rejected historical inputs."""
import hashlib
import html
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_release_docs import check_paths, check_text, check_zip

NAME = "\u004d\u0065\u0064\u0068\u0061\u0074"
ARABIC_NAME = "\u0645\u062f\u062d\u062a"

class ReleaseDocsTests(unittest.TestCase):
    def test_rejects_names_and_private_locations_without_echoing_content(self):
        samples = [NAME, ARABIC_NAME, "/Users/" + "tester/Documents/private",
                   "C:\\" + "Users\\tester\\Desktop\\private",
                   "owner " + "workspace work/" + "windows151/VALIDATION.json",
                   "outputs/" + "Agmad_Silent_Cutter_Release_1.5.1_Review"]
        for sample in samples:
            with self.subTest(sample=sample):
                failures = check_text("README.md", sample.encode())
                self.assertTrue(failures)
                self.assertNotIn(sample, "\n".join(failures))

    def test_keeps_technical_paths_and_licenses_usable(self):
        samples = [b"~/Library/Application Support/Agmad Silent Cutter",
                   b"%LOCALAPPDATA%\\Agmad Silent Cutter", b"/path/to/runtime",
                   b"/Users/<username>/Downloads", b"/home/runner/work/project",
                   (ROOT / "LICENSE").read_bytes(),
                   (ROOT / "THIRD_PARTY_NOTICES.md").read_bytes()]
        for sample in samples:
            self.assertEqual(check_text("public.md", sample), [])

    def test_missing_or_unreadable_document_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                check_paths([Path(temp) / "missing.md"])
            path = Path(temp) / "README.md"
            path.write_bytes(b"\xff\xfe")
            with self.assertRaises(UnicodeError):
                check_paths([path])

    def test_archive_checks_html_json_and_member_names(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("package/README_AR.html", ARABIC_NAME)
            archive.writestr("package/manifest.json", json.dumps({"path": "work/" + "export151/result"}))
            archive.writestr(NAME + "/notes.txt", "ordinary notes")
        with zipfile.ZipFile(buffer) as archive:
            failures = check_zip(archive)
        self.assertEqual(len(failures), 3)

class PackagingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir()
        for name in ["scripts", "docs", "windows/assets", "runtime"]:
            (self.repo / name).mkdir(parents=True, exist_ok=True)
        for name in ["check_release_docs.py", "package_windows.py", "package_source.py"]:
            shutil.copy2(ROOT / "scripts" / name, self.repo / "scripts" / name)
        shutil.copy2(ROOT / "scripts/package_macos.sh", self.repo / "scripts/package_macos.sh")
        for path, text in {
            "VERSION": "1.5.1\n", "LICENSE": "MIT License\n",
            "THIRD_PARTY_NOTICES.md": "Required notices\n",
            "README.md": "Public source instructions\n",
            "docs/PACKAGE_WINDOWS.ar.md": "دليل نظيف <PNG>\n",
            "docs/PACKAGE_MAC.md": "Clean Mac instructions\n",
            "docs/VALIDATION.md": "Dated test limits\n",
            "windows/THIRD_PARTY_NOTICES.md": "Windows notices\n",
            "windows/assets/build-info.json": "{}",
            "windows/assets/runtime-sha256.json": "{}",
        }.items():
            (self.repo / path).write_text(text, encoding="utf-8")
        self.output = Path(self.temp.name) / "output"

    def run_script(self, name, *args):
        return subprocess.run([sys.executable, str(self.repo / "scripts" / name), *map(str, args)],
                              capture_output=True, text=True)

    def windows(self, *extra):
        return self.run_script("package_windows.py", "--output", self.output,
                               "--runtime", self.repo / "runtime", *extra)

    def test_windows_archive_uses_clean_guide_and_preserves_license(self):
        result = self.windows()
        self.assertEqual(result.returncode, 0, result.stderr)
        path = self.output / "Agmad_Silent_Cutter_Windows_1.5.1.zip"
        with zipfile.ZipFile(path) as archive:
            base = "Agmad_Silent_Cutter_Windows_1.5.1/"
            text = (self.repo / "docs/PACKAGE_WINDOWS.ar.md").read_text(encoding="utf-8")
            self.assertEqual(archive.read(base + "README_AR.md").decode(), text)
            self.assertIn(html.escape(text), archive.read(base + "README_AR.html").decode())
            self.assertEqual(archive.read(base + "LICENSE"), (self.repo / "LICENSE").read_bytes())
            self.assertEqual(check_zip(archive), [])
        self.assertTrue(path.with_name(path.name + ".sha256").read_text().startswith(
            hashlib.sha256(path.read_bytes()).hexdigest()))

    def test_custom_windows_docs_rejected_before_staging(self):
        for option in ["--readme", "--validation"]:
            bad = self.repo / "bad.md"
            bad.write_text(NAME, encoding="utf-8")
            result = self.windows(option, bad)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(self.output.exists())
            self.assertNotIn(NAME, result.stderr)

    def test_windows_existing_archive_is_preserved(self):
        self.output.mkdir()
        existing = self.output / "Agmad_Silent_Cutter_Windows_1.5.1.zip"
        existing.write_bytes(b"existing release bytes")
        result = self.windows()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(existing.read_bytes(), b"existing release bytes")
        self.assertFalse((self.output / "Agmad_Silent_Cutter_Windows_1.5.1").exists())

    def test_windows_staged_extra_doc_rejected_before_zip(self):
        (self.repo / "runtime/extra.txt").write_text(ARABIC_NAME, encoding="utf-8")
        result = self.windows()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(list(self.output.glob("*.zip")))

    @unittest.skipUnless(shutil.which("bash"), "Bash required")
    def test_mac_dirty_guide_rejected_before_native_build(self):
        (self.repo / "docs/PACKAGE_MAC.md").write_text(NAME, encoding="utf-8")
        result = subprocess.run(["bash", str(self.repo / "scripts/package_macos.sh"), str(self.output)],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("personal attribution", result.stderr)
        self.assertFalse(list(self.output.glob("*.dmg")))
        self.assertFalse(list(self.output.glob("*.zip")))

    def commit_fixture(self):
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True, capture_output=True)
        subprocess.run(["git", "-c", "user.name=Package Test", "-c", "user.email=test@example.invalid",
                        "-c", "commit.gpgsign=false", "commit", "-qm", "fixture"],
                       cwd=self.repo, check=True, capture_output=True)

    @unittest.skipUnless(shutil.which("git"), "Git required")
    def test_source_uses_committed_docs_and_never_overwrites(self):
        self.commit_fixture()
        # Uncommitted edits must not silently change the recorded source snapshot.
        (self.repo / "README.md").write_text("uncommitted change\n")
        result = self.run_script("package_source.py", "--output", self.output)
        self.assertEqual(result.returncode, 0, result.stderr)
        path = self.output / "Agmad_Silent_Cutter_Source_1.5.1.zip"
        original = path.read_bytes()
        with zipfile.ZipFile(path) as archive:
            self.assertEqual(archive.read("Agmad_Silent_Cutter_Source_1.5.1/README.md"),
                             b"Public source instructions\n")
            self.assertEqual(archive.read("Agmad_Silent_Cutter_Source_1.5.1/LICENSE"), b"MIT License\n")
        result = self.run_script("package_source.py", "--output", self.output)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(path.read_bytes(), original)

    @unittest.skipUnless(shutil.which("git"), "Git required")
    def test_source_rejects_dirty_committed_documentation(self):
        (self.repo / "README.md").write_text(NAME, encoding="utf-8")
        self.commit_fixture()
        result = self.run_script("package_source.py", "--output", self.output)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.output.exists())
        self.assertNotIn(NAME, result.stderr)

if __name__ == "__main__":
    unittest.main()
