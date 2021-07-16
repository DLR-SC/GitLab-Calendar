<!-- 
SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)

SPDX-License-Identifier: MIT
-->

# GitCalendar
Tool that generates an ICS file from issues, milestones and iterations, of one or more GitLab projects. 
Only events with a due date are considered.

## Setup
The script requires Python >= 3.6 and uses the libraries [ics](https://icspy.readthedocs.io/en/stable/) ([Apache License v2.0](LICENSES/Apache-2.0.txt)) and
[python-gitlab](https://python-gitlab.readthedocs.io/en/stable/) ([LGPL v3.0](LICENSES/LGPL-3.0-only.txt)).
You can install it from [PyPi](https://pypi.org/) with the following command:

```shell
pip install gitcalendar
```

## Usage
There are two options of running the script:

### Run it with a config 
* Rename [gitlab-config.ini.example](gitlab-config.ini.example) to `gitlab-config.ini` and fit to your needs 
* Make sure that all wanted variables are given
* Make sure to declare your private token, a valid project or group id, and the path where your calendar files should be generated at.
 
Once this is done, you can run the script as follows:

```shell
gitcalendar --config <PATH OF YOUR CONFIG>    
```

### Run it with all the options you need
**Warning! Please consider using the prior option for not leaking any access tokens**
* Here, there's a need to declare the url of the gitlab instance, your private token, and at least one project or group id.

```shell
gitcalendar -u <URL> -t <PRIVATE TOKEN> -p <LIST OF PROJECT IDS> -g <LIST OF GROUP IDS>    
```

For more options please use:

```shell
gitcalendar -h
```

## Development
After you cloned the repository and changed into it, you can
perform the following actions. 

### Setup

Install with pip as follows:

```shell
pip install -e .[develop]
```

### Package Build
You can build a source package with the following command:
```shell
python setup.py sdist
```

You can build a wheel with the following command:
```shell
python setup.py bdist
```

## Changes

Please see the [CHANGELOG.md](CHANGELOG.md) for notable changes.

## Contributing

Please see the [CONTRIBUTING.md](CONTRIBUTING.md) if you want to contribute.

## Contributors

Please see [CONTRIBUTORS.md](CONTRIBUTORS.md) for further information about the contributors.

## License

Please see [LICENSE.md](LICENSE.md) for further information about how the content is licensed.

