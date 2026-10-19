import json
import os
import shutil
import tempfile
import unittest

from src.streamstats import __main__, parsers, report


class BaseTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.out = os.path.join(self.tmp, "REPORT.json")

        parsers.msgs.clear()
        report.timestamps.clear()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def make_file(self, name, text):
        path = os.path.join(self.tmp, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def run_cli(self, *args):
        argv = ["analyze", *args, "--output", self.out]
        return __main__.main(argv)

    def read_report(self):
        with open(self.out, "r", encoding="utf-8") as f:
            return json.load(f)


class TestUnicode(BaseTest):

    def test_csv_with_cyrillic(self):
        path = self.make_file(
            "ru.csv",
            "timestamp,name,message\n"
            "2024-01-01T10:00:00Z,Ivan,Привет мир\n"
            "2024-01-01T10:00:01Z,Michael,Goodbye world\n",
        )

        code = self.run_cli(path, "--format", "csv", "--skip-invalid")
        self.assertEqual(code, 0)

        with open(self.out, "r", encoding="utf-8") as f:
            raw = f.read()

        self.assertIn("Привет мир", raw)
        self.assertNotIn("\\u041f", raw)

    def test_jsonl_with_unicode(self):
        line1 = json.dumps(
            {
                "timestamp": "2024-01-01T10:00:00Z",
                "name": "Bubsich",
                "message": "日本語",
            },
        )
        line2 = json.dumps(
            {
                "timestamp": "2024-01-01T10:00:01Z",
                "name": "Macron",
                "message": "français",
            },
        )
        path = self.make_file("uni.jsonl", line1 + "\n" + line2 + "\n")

        code = self.run_cli(path, "--format", "jsonl", "--skip-invalid")
        self.assertEqual(code, 0)

        with open(self.out, "r", encoding="utf-8") as f:
            raw = f.read()

        self.assertIn("日本語", raw)
        self.assertIn("français", raw)

    def test_unicode_source_in_report(self):
        path = self.make_file(
            "файл.csv",
            "timestamp,level,message\n2024-01-01T10:00:00Z,INFO,ok\n",
        )

        code = self.run_cli(path, "--format", "csv")
        self.assertEqual(code, 0)

        report_data = self.read_report()
        sources = " ".join(item["source"] for item in report_data)
        self.assertIn("файл.csv", sources)


class TestCLI(BaseTest):

    def test_valid_csv_returns_zero(self):
        path = self.make_file(
            "ok.csv",
            "timestamp,name,message\n" "2024-01-01T10:00:00Z,Lobanov,hello\n",
        )

        code = self.run_cli(path, "--format", "csv")
        self.assertEqual(code, 0)

        self.assertTrue(os.path.exists(self.out))

        report_data = self.read_report()

        self.assertIsInstance(report_data, list)

        messages = " ".join(item["message"] for item in report_data)
        self.assertIn("Analyzing ended", messages)

    def test_invalid_csv_without_skip_returns_two(self):

        path = self.make_file(
            "bad.csv",
            "name,message\n" "2022,Romanenko,oops\n",
        )

        code = self.run_cli(path, "--format", "csv")
        self.assertEqual(code, 2)

    def test_invalid_csv_with_skip_returns_zero(self):

        path = self.make_file(
            "bad.csv",
            "timestamp,name,message\n"
            "20222-13-01,name,oops\n"
            "2024-01-01T10:00:00Z,Bykov,ok\n",
        )

        code = self.run_cli(path, "--format", "csv", "--skip-invalid")
        self.assertEqual(code, 0)

        report_data = self.read_report()
        levels = [item["level"] for item in report_data]
        self.assertIn("WARNING", levels)

    def test_empty_csv_returns_two(self):
        path = self.make_file("empty.csv", "")

        code = self.run_cli(path, "--format", "csv", "--skip-invalid")
        self.assertEqual(code, 2)

    def test_missing_file_returns_two(self):
        path = os.path.join(self.tmp, "no_such_file.csv")

        code = self.run_cli(path, "--format", "csv", "--skip-invalid")
        self.assertEqual(code, 2)

    def test_wrong_format_returns_two(self):
        path = self.make_file("x.csv", "a,b\n1,2\n")

        code = self.run_cli(path, "--format", "jsonl", "--skip-invalid")
        self.assertEqual(code, 2)

    def test_valid_jsonl_returns_zero(self):
        line = json.dumps(
            {"timestamp": "2024-01-01T10:00:00Z", "name": "Kupitman", "message": "hi"},
            ensure_ascii=False,
        )
        path = self.make_file("ok.jsonl", line + "\n")

        code = self.run_cli(path, "--format", "jsonl")
        self.assertEqual(code, 0)
        self.assertTrue(os.path.exists(self.out))

    def test_output_file_appends(self):

        path = self.make_file(
            "ok.csv",
            "timestamp,name,message\n" "2024-01-01T10:00:00Z,Raivo,a\n",
        )

        code1 = self.run_cli(path, "--format", "csv")
        self.assertEqual(code1, 0)
        first_len = len(self.read_report())

        parsers.msgs.clear()
        report.timestamps.clear()

        code2 = self.run_cli(path, "--format", "csv")
        self.assertEqual(code2, 0)
        second_len = len(self.read_report())

        self.assertGreater(second_len, first_len)


if __name__ == "__main__":
    unittest.main()
