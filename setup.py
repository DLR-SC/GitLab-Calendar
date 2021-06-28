# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

import setuptools

INSTALL_REQUIRES = [
    "python-gitlab >= 2.5.0",
    "ics >= 0.7",
]

DEVELOP_REQUIRES = [
    "reuse>=0.12.1",
    "wheel",
]

TESTS_REQUIRE = [
    "pytest>=6.2",
]

EXTRAS_REQUIRE = {
    "test": TESTS_REQUIRE,
    "develop": DEVELOP_REQUIRES + TESTS_REQUIRE,
}


package = setuptools.find_packages()

setuptools.setup(
    name="gitcalendar",
    version="0.1",
    author="Benjamin Moritz Bauer",
    author_email="benjamin.bauer@dlr.de",
    maintainer="Deutsches Zentrum fuer Luft- und Raumfahrt e.V. (DLR)",
    description="Tool that generates ics-files from a repositories issues,"
                " milestones and iterations, which have a due date.",
    url="https://github.com/DLR-SC/gitcalendar",
    license='License :: MIT',
    packages=package,
    entry_points={
        'console_scripts': [
            'gitcalendar=gitcalendar.gitcalendar:cli',
        ],
    },
    classifiers=[
        "Development Status :: 1 - Alpha"
        "Programming Language :: Python :: 3.6.8",

    ],
    keywords='ics ical calendar icalendar gitlab api outlook issues milestones',
    python_requires=">=3.6",
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRE,
    extras_require=EXTRAS_REQUIRE,
)
