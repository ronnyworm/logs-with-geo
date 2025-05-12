import pytest
import main
import os


testlog = "tests/test.log"
testinputfile1 = "tests/examples/access.log"
testinputfile1_lastline = "tests/examples/access.last_line"
testinputfile2 = "tests/examples/other_vhosts_access.log"
testinputfile2_lastline = "tests/examples/other_vhosts_access.last_line"


@pytest.fixture(autouse=True)
def run_around_tests():
    if os.path.isfile(testlog):
        os.remove(testlog)
    if os.path.isfile(testinputfile2_lastline):
        os.remove(testinputfile2_lastline)
    if os.path.isfile(testinputfile1_lastline):
        os.remove(testinputfile1_lastline)

    yield


class TestMainFlow:
    def test_no_args(self, capsys, monkeypatch):
        monkeypatch.setattr("sys.argv", ["main.py"])

        with pytest.raises(SystemExit) as e:
            main.main(how_often=1)
        assert e.value.code == 1

    def test_main_output(self, capsys, monkeypatch):
        monkeypatch.setattr("sys.argv", ["main.py", "-f", testinputfile2, "-o", testlog])
        main.main(how_often=1)
        captured = capsys.readouterr()
        assert "Processed remaining " in captured.out
        assert "lines from " + testinputfile2 in captured.out
        assert "Processed remaining 0 lines from " + testinputfile2 not in captured.out
        assert os.path.isfile(testinputfile2_lastline)

    def test_main_output_several_runs(self, capsys, monkeypatch):
        monkeypatch.setattr("sys.argv", ["main.py", "-f", testinputfile2, "-o", testlog, "-i", "1"])
        main.main(how_often=2)
        captured = capsys.readouterr()
        assert "Processed remaining 0 lines from " + testinputfile2 in captured.out
        assert os.path.isfile(testinputfile2_lastline)

    def test_main_output_just_once_if_interval_minus_1(self, capsys, monkeypatch):
        monkeypatch.setattr("sys.argv", ["main.py", "-f", testinputfile2, "-o", testlog, "-i", "-1"])
        main.main()
        captured = capsys.readouterr()
        assert "Processed remaining 0 lines from " + testinputfile2 not in captured.out
        assert os.path.isfile(testinputfile2_lastline)

    def test_main_output_ip_field1(self, capsys, monkeypatch):
        monkeypatch.setattr("sys.argv", ["main.py", "-f", testinputfile1, "-o", testlog, "-i", "-1", "--ipfield", "1"])
        main.main()
        captured = capsys.readouterr()
        assert "Processed remaining 0 lines from " + testinputfile1 not in captured.out
        assert os.path.isfile(testinputfile1_lastline)

    def test_main_output_ip_field1_nginx_guess(self, capsys, monkeypatch):
        monkeypatch.setattr("sys.argv", ["main.py", "-f", testinputfile1, "-o", testlog, "-i", "-1", "--type", "nginx"])
        main.main()
        captured = capsys.readouterr()
        assert "Processed remaining 0 lines from " + testinputfile1 not in captured.out
        assert os.path.isfile(testinputfile1_lastline)
