import setuptools

with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()

setuptools.setup(
    name="horen4gim-baue_bn",
    version="0.1",
    author="Benjamin Moritz Bauer",
    author_email="benjamin.bauer@dlr.de",
    description="Extension for GitLab, that generates ics-files from a repositories issues,"
                " milestones and iterations, which have a due date.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.dlr.de/sc/ivs-open/horen4gim",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.9",

    ],
    keywords='ics ical calendar icalendar gitlab api outlook issues milestones',
    python_requires='>=3.9',
)
