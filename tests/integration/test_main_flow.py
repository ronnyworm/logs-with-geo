import pytest
import main
import os


test_result_apache = "tests/apache_test.log"
test_result_nginx = "tests/nginx_test.log"
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


def count_not_found(err_out):
    return len([w for w in err_out.split("\n") if "not found" in w])


@pytest.fixture(autouse=True)
def run_around_tests():
    if os.path.isfile(test_result_apache):
        os.remove(test_result_apache)
    if os.path.isfile(test_result_nginx):
        os.remove(test_result_nginx)
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
        monkeypatch.setattr("sys.argv", ["main.py", "-f", log_file, "-o", test_result_apache])
        main.main(how_often=1)
        captured = capsys.readouterr()
        assert os.path.isfile(line_file(log_file))
        assert file_content(line_file(log_file)) == "1"
        os.remove(line_file(log_file))
        assert f"Processed remaining 1 lines from {log_file}" in captured.out
        assert count_not_found(captured.err) == 0
        assert 'country:"Spain" city:"Palma"' in file_content(test_result_apache)
        assert os.path.isfile(test_result_apache)

    def test_main_output_just_one_line_with_location_not_found(self, capsys, monkeypatch):
        log_file = testinputfile_just_one_line_unknown
        monkeypatch.setattr("sys.argv", ["main.py", "-f", log_file, "-o", test_result_apache])
        main.main(how_often=1)
        captured = capsys.readouterr()
        assert os.path.isfile(line_file(log_file))
        assert file_content(line_file(log_file)) == "1"
        os.remove(line_file(log_file))
        assert f"Processed remaining 1 lines from {log_file}" in captured.out
        assert count_not_found(captured.err) == 1
        assert 'country:"" city:""' in file_content(test_result_apache)
        assert os.path.isfile(test_result_apache)

    def test_main_output_full_file(self, capsys, monkeypatch):
        log_file = testinputfile_apache
        monkeypatch.setattr("sys.argv", ["main.py", "-f", log_file, "-o", test_result_apache])
        main.main(how_often=1)
        captured = capsys.readouterr()
        assert f"Processed remaining {line_count(log_file)} lines from {log_file}" in captured.out
        assert count_not_found(captured.err) == 20
        assert os.path.isfile(line_file(log_file))
        assert os.path.isfile(test_result_apache)
        assert file_content(line_file(log_file)) == "200"

    def test_main_output_several_runs(self, capsys, monkeypatch):
        log_file = testinputfile_apache
        monkeypatch.setattr("sys.argv", ["main.py", "-f", log_file, "-o", test_result_apache, "-i", "1"])
        main.main(how_often=2)
        captured = capsys.readouterr()
        assert "Processed remaining 0 lines from " + log_file in captured.out
        assert count_not_found(captured.err) == 20
        assert os.path.isfile(line_file(log_file))
        assert file_content(line_file(log_file)) == "200"

    def test_main_output_just_once_if_interval_minus_1(self, capsys, monkeypatch):
        log_file = testinputfile_apache
        monkeypatch.setattr("sys.argv", ["main.py", "-f", log_file, "-o", test_result_apache, "-i", "-1"])
        main.main()
        captured = capsys.readouterr()
        assert f"Processed remaining {line_count(log_file)} lines from {log_file}" in captured.out
        assert count_not_found(captured.err) == 20
        assert os.path.isfile(line_file(log_file))
        assert file_content(line_file(log_file)) == "200"

    def test_main_output_ip_field1_1(self, capsys, monkeypatch):
        log_file = testinputfile_nginx
        monkeypatch.setattr("sys.argv", ["main.py", "-f", log_file, "-o", test_result_apache, "-i", "-1", "--ipfield", "1"])
        main.main()
        captured = capsys.readouterr()
        assert f"Processed remaining {line_count(log_file)} lines from {log_file}" in captured.out
        assert count_not_found(captured.err) == 94
        assert os.path.isfile(line_file(log_file))
        assert file_content(line_file(log_file)) == "200"

    def test_main_output_ip_field1_nginx_guess(self, capsys, monkeypatch):
        log_file = testinputfile_nginx
        monkeypatch.setattr("sys.argv", ["main.py", "-f", log_file, "-o", test_result_nginx, "-i", "-1"])
        main.main()
        captured = capsys.readouterr()
        assert f"Processed remaining {line_count(log_file)} lines from {log_file}" in captured.out
        assert count_not_found(captured.err) == 94
        assert os.path.isfile(line_file(log_file))
        assert file_content(line_file(log_file)) == "200"

    def test_main_output_ip_field1_nginx_explicit(self, capsys, monkeypatch):
        log_file = testinputfile_nginx
        monkeypatch.setattr("sys.argv", ["main.py", "-f", log_file, "-o", test_result_nginx, "-i", "-1", "--type", "nginx"])
        main.main()
        captured = capsys.readouterr()
        assert f"Processed remaining {line_count(log_file)} lines from {log_file}" in captured.out
        assert count_not_found(captured.err) == 94
        assert os.path.isfile(line_file(log_file))
        assert file_content(line_file(log_file)) == "200"
