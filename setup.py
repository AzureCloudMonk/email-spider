# Automatically created by: shub deploy

from setuptools import setup, find_packages

setup(
    name         = 'emailSpider',
    version      = '1.0',
    packages     = find_packages(),
    package_data={
        'emailSpider': ['alexa-1000-to-10000-scrapinghub.csv']
    },
    entry_points = {'scrapy': ['settings = emailSpider.settings']},
    zip_safe=False,
)
