# Automatically created by: shub deploy

from setuptools import setup, find_packages

setup(
    name         = 'emailSpider',
    version      = '1.0',
    packages     = find_packages(),
    package_data={
        'emailSpider': ['data/input/*.csv', 'scripts/*.lua']
    },
    entry_points = {'scrapy': ['settings = emailSpider.settings']},
    zip_safe=False,
)
