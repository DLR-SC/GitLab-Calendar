# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

import setuptools
import pathlib

INSTALL_REQUIRES = [
    "python-gitlab >= 2.5.0",
    "ics >= 0.7",
]

DEVELOP_REQUIRES = [
    "reuse>=0.12.1",
    "wheel",
    "twine",
]

TESTS_REQUIRE = [
    "pytest>=6.2",
]

EXTRAS_REQUIRE = {
    "test": TESTS_REQUIRE,
    "develop": DEVELOP_REQUIRES + TESTS_REQUIRE,
}


package = setuptools.find_packages()

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setuptools.setup(
    name="gitcalendar",
    version="0.9",
    author="Benjamin Moritz Bauer",
    author_email="benjamin.bauer@dlr.de",
    maintainer="Deutsches Zentrum fuer Luft- und Raumfahrt e.V. (DLR)",
    description="Tool that generates ics-files from a repositories issues,"
                " milestones and iterations, which have a due date.",
    long_description=README,
    long_description_content_type='text/markdown',
    url="https://gitlab.com/dlr-sc/gitcalendar",
    license='License :: MIT',
    packages=package,
    entry_points={
        'console_scripts': [
            'gitcalendar=gitcalendar.gitcalendar:cli',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.6",

    ],
    keywords=[
        'ics',
        'ical',
        'calendar',
        'icalendar',
        'gitlab',
    ],
    python_requires=">=3.6",
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRE,
    extras_require=EXTRAS_REQUIRE,
)
