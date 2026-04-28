import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "reviewflow.py"

spec = importlib.util.spec_from_file_location("reviewflow", SCRIPT)
reviewflow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reviewflow)


class ReviewflowTests(unittest.TestCase):
    def test_safe_slug(self):
        self.assertEqual(reviewflow.safe_slug("my review!"), "my_review")
        self.assertTrue(reviewflow.safe_slug("脑电 综述"))

    def test_intake_creates_stateful_project(self):
        with tempfile.TemporaryDirectory() as td:
            cmd = [
                sys.executable,
                str(SCRIPT),
                "intake",
                "--name",
                "demo",
                "--topic",
                "EEG review",
                "--output",
                td,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.assertIn("Prepared guided intake project", result.stdout)
            project = Path(td) / "demo"
            self.assertTrue((project / "intake" / "review_brief.md").exists())
            self.assertTrue((project / "protocol" / "review_protocol.md").exists())
            self.assertTrue((project / "notes" / "evidence_matrix.csv").exists())
            self.assertTrue((project / ".reviewflow" / "state.json").exists())
            self.assertTrue((project / "quality" / "codex_handoff.md").exists())

    def test_resume_marks_human_checkpoint(self):
        with tempfile.TemporaryDirectory() as td:
            init_cmd = [
                sys.executable,
                str(SCRIPT),
                "intake",
                "--name",
                "demo",
                "--topic",
                "EEG review",
                "--output",
                td,
            ]
            subprocess.run(init_cmd, capture_output=True, text=True, check=True)
            project = Path(td) / "demo"
            resume_cmd = [
                sys.executable,
                str(SCRIPT),
                "resume",
                "--project",
                str(project),
                "--mark",
                "zotero_imported",
                "--mark",
                "pdfs_checked",
            ]
            subprocess.run(resume_cmd, capture_output=True, text=True, check=True)
            state = json.loads((project / ".reviewflow" / "state.json").read_text(encoding="utf-8-sig"))
            self.assertTrue(state["checkpoints"]["zotero_imported"])
            self.assertTrue(state["checkpoints"]["pdfs_checked"])

    def test_audit_docx_minimal_zotero_fields(self):
        xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>
<w:p><w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText> ADDIN ZOTERO_ITEM CSL_CITATION </w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>(Smith, 2020)</w:t></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>
<w:p><w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText> ADDIN ZOTERO_BIBL </w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>Smith...</w:t></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>
</w:body></w:document>'''
        with tempfile.TemporaryDirectory() as td:
            docx = Path(td) / "test.docx"
            with zipfile.ZipFile(docx, "w") as z:
                z.writestr("word/document.xml", xml)
            cmd = [sys.executable, str(SCRIPT), "audit-docx", "--docx", str(docx)]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            report = json.loads(result.stdout)
            self.assertEqual(report["zotero_item_count"], 1)
            self.assertEqual(report["zotero_bibl_count"], 1)
            self.assertTrue(report["passes_basic_structure_check"])

    def test_final_check_reports_gaps_without_docx(self):
        with tempfile.TemporaryDirectory() as td:
            init_cmd = [
                sys.executable,
                str(SCRIPT),
                "intake",
                "--name",
                "demo",
                "--topic",
                "EEG review",
                "--output",
                td,
            ]
            subprocess.run(init_cmd, capture_output=True, text=True, check=True)
            project = Path(td) / "demo"
            cmd = [sys.executable, str(SCRIPT), "final-check", "--project", str(project)]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            report = json.loads(result.stdout)
            self.assertFalse(report["ready_for_manual_submission_review"])
            self.assertTrue(report["remaining_gaps"])


if __name__ == "__main__":
    unittest.main()
