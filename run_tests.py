"""
Interactive cross-browser test runner.

Displays a menu to select which browsers to run tests on, then executes
tests in parallel across all selected browsers (one pytest subprocess per browser).
The pytest-xdist and pytest-html plugins are configured via config.py.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import config


BROWSERS: dict[int, dict] = {
    1: {"name": "firefox", "label": "Firefox", "available": True},
    2: {"name": "edge", "label": "Microsoft Edge", "available": True},
    3: {"name": "opera", "label": "Opera", "available": True},
    4: {
        "name": "webkit",
        "label": "WebKit (Safari)",
        "available": platform.system() == "Darwin",
    },
}


def _clear() -> None:
    """Clear the terminal screen."""
    subprocess.run(["cmd", "/c", "cls"] if os.name == "nt" else ["clear"])


def _show_menu(selected: set[int]) -> None:
    """Render the interactive selection menu."""
    _clear()
    print("=" * 56)
    print("        CROSS-BROWSER TEST RUNNER")
    print("=" * 56)
    print()
    print("  Select browsers to run tests on:")
    print()

    for key, info in BROWSERS.items():
        checked = "●" if key in selected else "○"
        if info["available"]:
            print(f"    [{checked}]  {key}. {info['label']}")
        else:
            print(f"    [ ]  {key}. {info['label']}  (not available on {platform.system()})")

    print()
    print("  [Enter]  → Start tests")
    print("  [Q]      → Quit")
    print()


def _get_key() -> str:
    """Get a single keypress on Windows, or a full line on other platforms."""
    try:
        import msvcrt  # Windows only
        return msvcrt.getwch()
    except ImportError:
        return input()


def select_browsers() -> list[str]:
    """Show the interactive menu and return the list of selected browser names."""
    selected: set[int] = set()

    while True:
        _show_menu(selected)
        key = _get_key()

        # Enter – confirm selection
        if key in ("\r", "\n"):
            if not selected:
                print("\n  ⚠  No browsers selected. Choose at least one, or press Q to quit.")
                print("  Press any key to continue.")
                _get_key()
                continue
            break

        # Q – quit
        if key in ("q", "Q"):
            print("\n  Aborted.")
            sys.exit(0)

        # Digit – toggle browser
        if key.isdigit():
            num = int(key)
            if num not in BROWSERS:
                continue

            info = BROWSERS[num]
            if not info["available"]:
                print(f"\n  ⚠  {info['label']} is not available on {platform.system()}.")
                print("     Please make a different choice.  Press any key to continue.")
                _get_key()
                continue

            if num in selected:
                selected.remove(num)
            else:
                selected.add(num)

    return [BROWSERS[k]["name"] for k in sorted(selected)]


def _print_oversubscription_warning(browsers: list[str]) -> None:
    """Warn if total xdist workers exceed reasonable limits."""
    n = int(config.PARALLEL_PROCESSES) if config.PARALLEL_PROCESSES.isdigit() else 2
    total_workers = len(browsers) * n
    if total_workers > config.LOGICAL_CPUS:
        print(
            f"  ⚠  {len(browsers)} browsers × {n} workers = {total_workers} total, "
            f"but only {config.LOGICAL_CPUS} logical CPUs ({config.PHYSICAL_CPUS} physical cores)."
        )
        print("     This may cause severe oversubscription → timeouts & flaky tests.")
        print(f"     Reduce PARALLEL_PROCESSES in config.py or set PARALLEL_PROCESSES=2 env var.")
        print()


def _run_browser(browser_name: str) -> tuple[str, int]:
    """Run the full test suite for a single browser in a subprocess."""
    print(f"\n{'─' * 56}")
    print(f"  ▶  Starting tests on  {browser_name.upper()}")
    print(f"{'─' * 56}\n")

    report_dir = Path(config.HTML_REPORT_DIR)
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = str(report_dir / f"test_report_{browser_name}.html")

    # NOTE: reruns come from pyproject.toml, not repeated here.
    # This keeps the retry policy consistent across all run modes.
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/",
            "-v",
            "--tb=short",
            f"--browser={browser_name}",
            f"-n={config.PARALLEL_PROCESSES}",
            "--dist=loadscope",
            f"--html={report_path}",
            "--self-contained-html",
            "--enable-history",
        ],
    )
    return browser_name, result.returncode


def main() -> None:
    """Entry point: menu → parallel execution → summary."""
    browsers = select_browsers()

    print(f"\n  Running tests on:  {', '.join(b.upper() for b in browsers)}")
    print(f"  Parallel workers:  {len(browsers)}")
    print(f"  xdist per browser: {config.PARALLEL_PROCESSES}")
    print()

    _print_oversubscription_warning(browsers)

    results: dict[str, int] = {}
    with ThreadPoolExecutor(max_workers=len(browsers)) as pool:
        futures = {pool.submit(_run_browser, b): b for b in browsers}
        for future in as_completed(futures):
            name, code = future.result()
            results[name] = code

    # Summary
    print(f"\n{'=' * 56}")
    print("  RESULTS SUMMARY")
    print(f"{'=' * 56}")
    failed = 0
    for name in sorted(results):
        status = "✅ PASS" if results[name] == 0 else "❌ FAIL"
        print(f"    {name.upper():<14} {status}")
        if results[name] != 0:
            failed += 1

    print()
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
