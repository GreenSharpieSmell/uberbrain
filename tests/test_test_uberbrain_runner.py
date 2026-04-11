import sys
import types

import test_uberbrain


def test_convenience_runner_executes_full_suite(monkeypatch):
    captured = {}

    def fake_main(args):
        captured["args"] = list(args)
        return 0

    dummy_pytest = types.SimpleNamespace(main=fake_main)

    monkeypatch.setitem(sys.modules, "pytest", dummy_pytest)

    exit_code = test_uberbrain.main()

    assert exit_code == 0
    assert captured["args"] == ["-q", "tests"]
