<!-- 
SPDX-FileCopyrightText: 2021 German Aerospace Center (DLR)

SPDX-License-Identifier: MIT
-->

# GitCalendar
Tool that generates ics-files from a repositories issues, milestones and iterations, which have a due date.

## Setup
The script requires Python >= 3.9 and uses the libraries [ics](https://icspy.readthedocs.io/en/stable/) ([LGPL v3.0](Licenses/LGPL-3.0.txt)) and [python-gitlab](https://python-gitlab.readthedocs.io/en/stable/) ([Apache License v2.0.txt](Licenses/Apache-2.0.txt))
* Clone repository
* Change into repository
* install the [required dependencies](requirements.txt)


```
git clone ...
cd horen4gim 
pip install -r requirements.txt
```

## Usage
There are two options of running the script:
### 1 Run it with a config 
* Rename [gitlab-config.ini.example](gitlab-config.ini.example) to `gitlab-config.ini` and fit to your needs 
```
ren gitlab-config.ini.example gitlab-config.ini
```
* Make sure to declare your private token, a valid project or group id, and the path where your calendar files should be generated at.
* Once this is done, you can run the script as follows:
```
python src/horen4gim.py -c <PATH OF YOUR CONFIG>    
```

### 2 Run it with all the options you need
**Warning! Please consider using the config in first case for not leaking any access tokens**
* Here, there's a need to declare the url of the gitlab instance, your private token, and at least one project or group id.
```
python src/horen4gim.py -u <URL> -t <PRIVATE TOKEN> -p <LIST OF PROJECT IDS> -g <LIST OF GROUP IDS>    
```
* For more options please use:
```
python src/horen4gim.py -h
```
