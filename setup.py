from setuptools import setup, find_packages


setup(
    name='loom',
    version='0.1',
    description="Map database queries to JSON schema objects.",
    long_description="",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ],
    keywords='schema jsonschema json data sql etl loader elasticsearch',
    author='OCCRP',
    author_email='tech@occrp.org',
    url='http://github.com/occrp/loom',
    license='AGPLv3',
    packages=find_packages(exclude=['ez_setup', 'examples', 'test']),
    namespace_packages=[],
    package_data={},
    include_package_data=True,
    zip_safe=False,
    test_suite='nose.collector',
    install_requires=[
        'jsonmapping',
        'sqlalchemy',
        'elasticsearch',
        'pyyaml',
        'psycopg2',
        'unicodecsv',
        'click',
        'six',
        'normality'
    ],
    tests_require=[
        'nose',
        'coverage',
        'dataset',
    ],
    entry_points={
        'console_scripts': [
            'loom = loom.cli:cli'
        ]
    }
)
