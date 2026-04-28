import re


def parse_log(log: str) -> dict[str, str]:
    """Parse test runner output into per-test results.

    Args:
        log: Full stdout+stderr output of `bash run_test.sh 2>&1`.

    Returns:
        Dict mapping test_id to status.
        - test_id: pytest native format with xdist group suffix stripped
          (e.g. "tests/foo.py::TestClass::test_func[param]")
        - status: one of "PASSED", "FAILED", "SKIPPED", "ERROR"
    """
    results = {}

    # Strip ANSI escape codes
    log = re.sub(r'\x1b\[[0-9;]*m', '', log)

    # pytest-xdist inline format:
    #   [gwN] [ XX%] STATUS tests/path.py::test_name[param with spaces]@group
    # Test id may contain spaces (e.g. parameterized with filenames).
    # The optional @word suffix at end of line is the xdist_group marker.
    xdist_pattern = re.compile(
        r'^\[gw\d+\]\s+\[\s*\d+%\]\s+(PASSED|FAILED|SKIPPED|ERROR|XFAIL|XPASS)\s+(.+?)\s*$',
        re.MULTILINE
    )
    for m in xdist_pattern.finditer(log):
        status_raw = m.group(1)
        test_id_raw = m.group(2).strip()
        # Strip xdist_group suffix (e.g. @static_files, @unix_socket)
        test_id = re.sub(r'@\w+$', '', test_id_raw)
        status = _normalize_status(status_raw)
        results.setdefault(test_id, status)

    # pytest summary short lines: "FAILED tests/path.py::test_name - reason"
    # (used as fallback for non-xdist or collection errors)
    summary_pattern = re.compile(
        r'^(PASSED|FAILED|SKIPPED|ERROR|XFAIL|XPASS)\s+(tests/\S+?)(?:\s+-.*)?$',
        re.MULTILINE
    )
    for m in summary_pattern.finditer(log):
        status_raw, test_id = m.group(1), m.group(2)
        test_id = re.sub(r'@\w+$', '', test_id)
        status = _normalize_status(status_raw)
        results.setdefault(test_id, status)

    return results


def _normalize_status(raw: str) -> str:
    return {
        'PASSED': 'PASSED',
        'FAILED': 'FAILED',
        'SKIPPED': 'SKIPPED',
        'ERROR': 'ERROR',
        'XFAIL': 'SKIPPED',
        'XPASS': 'PASSED',
    }.get(raw, raw)

