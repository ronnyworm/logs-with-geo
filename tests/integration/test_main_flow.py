import pytest
import main
import os


testlog = "tests/test.log"
testinput = "tests/examples/other_vhosts_access.log"


class TestMainFlow:
    def test_no_args(self, capsys, monkeypatch):
        monkeypatch.setattr("sys.argv", ["main.py"])

        with pytest.raises(SystemExit) as e:
            main.main()
        assert e.value.code == 1

    def test_main_output(self, capsys, monkeypatch):
        if os.path.isfile(testlog):
            os.remove(testlog)
        if os.path.isfile(testinput + ".last_line"):
            os.remove(testlog + ".last_line")
        monkeypatch.setattr("sys.argv", ["main.py", "-f", testinput, "-o", testlog])
        main.main()
        captured = capsys.readouterr()
        assert "Processed remaining " in captured.out
        assert "lines from tests" in captured.out
        assert "Processed remaining 0 lines from tests" not in captured.out
