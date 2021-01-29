# Horen4GIM

Extension for GitLab, that generates ics-files from a repositories issues, milestones and iterations, which have a due date.

## Setup
* Clone repository
* Change into repository

```
pip install -r requirements.txt
```

* Rename config file to "gitlab-config.ini" and fit to your needs 
* Make sure to declare  your private token, a valid project or group id, and the path where your calendar files should be generated at.
```
mv gitlab-config.ini.example gitlab-config.ini
```
