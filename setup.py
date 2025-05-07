from setuptools import setup, find_packages

setup(
    name="terrafedash",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "plotly>=5.0.0",
        "streamlit>=1.10.0",
        "altair>=4.0.0",
        "pydeck>=0.7.0",
        "protobuf>=3.19.0",
        "python-dateutil>=2.8.0",
        "pytz>=2021.1",
        "requests>=2.25.0",
        "tornado>=6.1.0",
        "watchdog>=2.1.0"
    ],
) 