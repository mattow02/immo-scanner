import subprocess
import sys
import platform

def build():
    name = "immo-scanner"
    system = platform.system().lower()

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", name,
        "--collect-all", "playwright",
        "--collect-all", "playwright_stealth",
        "--collect-all", "fake_useragent",
        "--collect-all", "curl_cffi",
        "--collect-all", "certifi",
        "--hidden-import", "lxml",
        "--hidden-import", "lxml.etree",
        "--hidden-import", "lxml._elementpath",
        "--hidden-import", "cloudscraper",
        "--hidden-import", "requests_toolbelt",
        "--hidden-import", "charset_normalizer",
        "--hidden-import", "immo_scanner.scrapers.leboncoin",
        "--hidden-import", "immo_scanner.scrapers.seloger",
        "--hidden-import", "immo_scanner.scrapers.bienici",
        "--hidden-import", "immo_scanner.scrapers.pap",
        "--hidden-import", "immo_scanner.scrapers.laforet",
        "--hidden-import", "immo_scanner.scrapers.orpi",
        "--hidden-import", "immo_scanner.scrapers.figaro",
        "--exclude-module", "tkinter",
        "--exclude-module", "unittest",
        "--exclude-module", "test",
        "immo_scanner/cli.py",
    ]

    print(f"Building {name} for {system}...")
    subprocess.run(cmd, check=True)
    ext = ".exe" if system == "windows" else ""
    print(f"\nDone! Binary: dist/{name}{ext}")

if __name__ == "__main__":
    build()
