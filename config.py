import os


try:
    import psutil
    LOGICAL_CPUS = psutil.cpu_count(logical=True)
    PHYSICAL_CPUS = psutil.cpu_count(logical=False)
except Exception:
    LOGICAL_CPUS = 8
    PHYSICAL_CPUS = 4


BASE_URL = os.getenv("BASE_URL", "https://practice-automation.com/")
DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "10"))
SHORT_TIMEOUT = int(os.getenv("SHORT_TIMEOUT", "3"))
LONG_TIMEOUT = int(os.getenv("LONG_TIMEOUT", "20"))

# pytest-xdist: number of parallel processes per browser run.
#
# Capped to 2: 3 browsers × 2 workers = 6 concurrent workers, which is
# safely within your physical cores / logical threads.
# Can also be set via env var to an integer (e.g. PARALLEL_PROCESSES=4) or "auto", "logical", "cpu_count".
PARALLEL_PROCESSES = os.getenv("PARALLEL_PROCESSES", "2")

# pytest-html: output directory for HTML test reports.
HTML_REPORT_DIR = os.getenv("HTML_REPORT_DIR", "reports")

# Password used for password-protected downloads on practice-automation.com
DOWNLOAD_PASSWORD = os.getenv("DOWNLOAD_PASSWORD", "automateNow")
