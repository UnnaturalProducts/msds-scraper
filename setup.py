from setuptools import setup, find_packages 

setup(
    name="msds_scraper",
    version="0.0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "selenium==3.141.0",
        "urllib3==1.25.8",
        "xlrd >= 1.0.0",
        "pytest==5.4.2",
        "pandas",
        "webdriver-manager",
        "tqdm",
        "openpyxl"
    ], entry_points={
        'console_scripts': [
            'msds_scraper = msds_scraper.__main__:main',
        ]
    },
)
