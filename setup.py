from setuptools import setup, find_packages

setup(
    name="immo-scanner",
    version="1.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
        "openpyxl>=3.1.0",
        "rich>=13.0.0",
        "click>=8.1.0",
        "fake-useragent>=1.4.0",
        "playwright>=1.40.0",
        "playwright-stealth>=2.0.0",
        "curl_cffi>=0.7.0",
    ],
    entry_points={
        "console_scripts": [
            "immo-scanner=immo_scanner.cli:main",
        ],
    },
)
