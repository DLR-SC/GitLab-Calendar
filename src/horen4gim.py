
import gitlab
from settings import GITLAB_URL, GITLAB_ACCESS_TOKEN

if __name__ == "__main__":
    gl = gitlab.Gitlab(GITLAB_URL, GITLAB_ACCESS_TOKEN, ssl_verify=True)
    gl.auth()
    projects = gl.projects.list(owned=True)
    print(projects)

