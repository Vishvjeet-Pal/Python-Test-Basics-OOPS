import os
import pytest
from pathlib import Path
import importlib

# import the module under test
import python_test


def test_read_log_parses_lines(tmp_path):
    p = tmp_path / "log.txt"
    p.write_text("Error\t2021-01-01\tsrc1\nInformation\t2021-01-02\tsrc2\nmalformed line\n")
    logs = python_test.read_log(str(p))
    assert isinstance(logs, list)
    assert logs == [
        {"level": "Error", "date": "2021-01-01", "source": "src1"},
        {"level": "Information", "date": "2021-01-02", "source": "src2"},
    ]


def test_filter_logs_filters_error_and_critical():
    logs = [
        {"level": "Information", "date": "d1", "source": "s1"},
        {"level": "Error", "date": "d2", "source": "s2"},
        {"level": "Critical", "date": "d3", "source": "s3"},
    ]
    filtered = python_test.filter_logs(logs)
    levels = [r["level"] for r in filtered]
    assert "Error" in levels and "Critical" in levels
    assert "Information" not in levels


def test_read_log_missing_returns_empty():
    missing = python_test.read_log("this_file_does_not_exist_hopefully.txt")
    assert missing == []


def test_useranalytics_add_load_calculate_stats(tmp_path):
    p = tmp_path / "user_log.txt"
    analytics = python_test.UserAnalytics(str(p))
    # add valid records
    analytics.add_record("101 in")
    analytics.add_record("102 out")
    analytics.add_record("101 out")
    # load and compute
    analytics.load_file()
    stats = analytics.calculate_stats()
    assert stats["total_records"] == 3
    assert stats["user_activity"]["101"] == 2
    assert stats["user_activity"]["102"] == 1
    assert stats["action_frequency"]["in"] == 1
    assert stats["action_frequency"]["out"] == 2


def test_add_record_invalid_raises(tmp_path):
    p = tmp_path / "user_log2.txt"
    analytics = python_test.UserAnalytics(str(p))
    with pytest.raises(ValueError):
        analytics.add_record("invalid_format_line_with_no_space")


def test_generate_report_uses_pandas_like(monkeypatch, tmp_path):
    # Replace pandas.DataFrame with a dummy that records rows and writes a marker file
    class DummyDF:
        def __init__(self, rows):
            self.rows = rows

        def to_csv(self, filename, index=False):
            Path(filename).write_text("DUMMY_OK")

    class DummyPd:
        DataFrame = DummyDF

    monkeypatch.setattr(python_test, "pd", DummyPd)
    p = tmp_path / "user_log3.txt"
    analytics = python_test.UserAnalytics(str(p))
    analytics.add_record("201 in")
    analytics.add_record("202 out")
    analytics.load_file()
    out = tmp_path / "report.csv"
    analytics.generate_report(filename=str(out))
    assert out.exists()
    assert out.read_text() == "DUMMY_OK"