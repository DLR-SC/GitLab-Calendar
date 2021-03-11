# SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

import setuptools

with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()

package = setuptools.find_packages()

setuptools.setup(
    name="gitcalendar",
    version="0.1",
    author="Benjamin Moritz Bauer",
    author_email="benjamin.bauer@dlr.de",
    maintainer="Deutsches Zentrum fuer Luft- und Raumfahrt e.V. (DLR)",
    description="Tool that generates ics-files from a repositories issues,"
                " milestones and iterations, which have a due date.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DLR-SC/gitcalendar",
    license='License :: MIT',
    packages=package,
    entry_points={
        'console_scripts': [
            'gitcalendar=gitcalendar.gitcalendar:get_variables',
        ],
    },
    classifiers=[
        "Development Status :: 1 - Alpha"
        "Programming Language :: Python :: 3.9",

    ],
    keywords='ics ical calendar icalendar gitlab api outlook issues milestones',
    python_requires='>=3.9',
)
