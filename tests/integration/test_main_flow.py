import pytest
import main
import os


testlog = "tests/apache_test.log"
testinputfile_nginx = "tests/examples/access.log"
testinputfile_apache = "tests/examples/other_vhosts_access.log"
testinputfile_just_one_line = "tests/examples/other_vhosts_access1.log"
testinputfile_just_one_line_unknown = "tests/examples/other_vhosts_access1u.log"


def line_file(filename):
    return filename.replace(".log", ".last_line")


def file_content(filename):
    with open(filename, 'r') as f:
        return "\n".join(f.readlines())


def line_count(filename):
    with open(filename, 'r') as f:
        return len(f.readlines())


@pytest.fixture(autouse=True)
def run_around_tests():
    if os.path.isfile(testlog):
        os.remove(testlog)
    if os.path.isfile(line_file(testinputfile_apache)):
        os.remove(line_file(testinputfile_apache))
    if os.path.isfile(line_file(testinputfile_nginx)):
        os.remove(line_file(testinputfile_nginx))
    yield


class TestMainFlow:
    def test_no_args(self, capsys, monkeypatch):
        monkeypatch.setattr("sys.argv", ["main.py"])

        with pytest.raises(SystemExit) as e:
            main.main(how_often=1)
        assert e.value.code == 1

    def test_main_output_just_one_line_with_location_found(self, capsys, monkeypatch):
        log_file = testinputfile_just_one_line
        monkeypatch.setattr("sys.argv", ["main.py", "-f", log_file, "-o", testlog])
        main.main(how_often=1)
        captured = capsys.readouterr()

        assert os.path.isfile(line_file(log_file))
        os.remove(line_file(log_file))
        assert f"Processed remaining 1 lines from {log_file}" in captured.out
        assert 'country:"Spain" city:"Palma"' in file_content(testlog)
        assert os.path.isfile(testlog)

    def test_main_output_just_one_line_with_location_not_found(self, capsys, monkeypatch):
        log_file = testinputfile_just_one_line_unknown
        monkeypatch.setattr("sys.argv", ["main.py", "-f", log_file, "-o", testlog])
        main.main(how_often=1)
        captured = capsys.readouterr()

        assert os.path.isfile(line_file(log_file))
        os.remove(line_file(log_file))
        assert f"Processed remaining 1 lines from {log_file}" in captured.out
        assert 'country:"" city:""' in file_content(testlog)
        assert os.path.isfile(testlog)

    def test_main_output_full_file(self, capsys, monkeypatch):
        monkeypatch.setattr("sys.argv", ["main.py", "-f", testinputfile_apache, "-o", testlog])
        main.main(how_often=1)
        captured = capsys.readouterr()
        assert f"Processed remaining {line_count(testinputfile_apache)} lines from {testinputfile_apache}" in captured.out
        assert os.path.isfile(line_file(testinputfile_apache))
        assert os.path.isfile(testlog)

    def test_main_output_several_runs(self, capsys, monkeypatch):
        monkeypatch.setattr("sys.argv", ["main.py", "-f", testinputfile_apache, "-o", testlog, "-i", "1"])
        main.main(how_often=2)
        captured = capsys.readouterr()
        assert "Processed remaining 0 lines from " + testinputfile_apache in captured.out
        assert os.path.isfile(line_file(testinputfile_apache))

    def test_main_output_just_once_if_interval_minus_1(self, capsys, monkeypatch):
        monkeypatch.setattr("sys.argv", ["main.py", "-f", testinputfile_apache, "-o", testlog, "-i", "-1"])
        main.main()
        captured = capsys.readouterr()
        assert f"Processed remaining {line_count(testinputfile_apache)} lines from {testinputfile_apache}" in captured.out
        assert os.path.isfile(line_file(testinputfile_apache))

    def test_main_output_ip_field1(self, capsys, monkeypatch):
        monkeypatch.setattr("sys.argv", ["main.py", "-f", testinputfile_nginx, "-o", testlog, "-i", "-1", "--ipfield", "1"])
        main.main()
        captured = capsys.readouterr()
        assert f"Processed remaining {line_count(testinputfile_nginx)} lines from {testinputfile_nginx}" in captured.out
        assert os.path.isfile(line_file(testinputfile_nginx))

    def test_main_output_ip_field1_nginx_guess(self, capsys, monkeypatch):
        monkeypatch.setattr("sys.argv", ["main.py", "-f", testinputfile_nginx, "-o", testlog, "-i", "-1", "--type", "nginx"])
        main.main()
        captured = capsys.readouterr()
        assert f"Processed remaining {line_count(testinputfile_nginx)} lines from {testinputfile_nginx}" in captured.out
        assert os.path.isfile(line_file(testinputfile_nginx))
