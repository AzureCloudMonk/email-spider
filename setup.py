# Automatically created by: shub deploy

from setuptools import setup, find_packages

setup(
    name         = 'emailSpider',
    version      = '1.0',
    packages     = find_packages(),
    package_data={
        'emailSpider': ['alexa-top-10000-100000-shub.csv']
    },
    entry_points = {'scrapy': ['settings = emailSpider.settings']},
    zip_safe=False,
)
