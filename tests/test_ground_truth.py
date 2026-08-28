"""Reconstructing what actually happened, including edits made through the shell.

Both behaviours here were found by running against a real agent trace, not by
reasoning about the docs.
"""

from receipts.actions import actions
from receipts.shell import writes
from receipts.signals import command_failed


def test_shell_edits_count_as_file_writes(load):
    """A real agent edited source with `sed -i`; a file-tool-only view saw nothing."""
    written = [p for a in actions(load("real_claude_fix_source.ndjson")) for p in a.writes]
    assert "src/pricing.py" in written


def test_redirect_and_heredoc_targets_are_captured():
    assert writes("echo hi > out.txt") == ["out.txt"]
    assert writes("cat > tests/test_x.py <<'EOF'") == ["tests/test_x.py"]
    assert writes("tee -a logs/run.log") == ["logs/run.log"]


def test_stderr_redirection_is_not_a_file_write():
    assert writes(".venv/bin/pytest 2>&1 | tail -25") == []
    assert writes("ls -la && find . -type f") == []


def test_failure_is_read_from_output_when_a_pipe_masks_the_exit_code(load):
    """`pytest | tail` exits 0 even when the suite fails. Output outranks status."""
    failed = [
        a
        for a in actions(load("real_claude_fix_source.ndjson"))
        if a.kind == "run_command" and command_failed(a)
    ]
    assert failed, "the failing pytest run should be detected despite a zero exit code"
    assert "pytest" in failed[0].target
