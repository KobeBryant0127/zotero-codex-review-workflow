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

    def test_init_project(self):
        with tempfile.TemporaryDirectory() as td:
            cmd = [sys.executable, str(SCRIPT), "init", "--name", "demo", "--topic", "EEG review", "--output", td]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.assertIn("Created review project", result.stdout)
            project = Path(td) / "demo"
            self.assertTrue((project / "protocol" / "review_protocol.md").exists())
            self.assertTrue((project / "notes" / "evidence_matrix.csv").exists())

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


if __name__ == "__main__":
    unittest.main()
