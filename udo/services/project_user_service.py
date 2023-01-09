from udo.models.ProjectUser import UdoProjectUser
from udo.models.Project import UdoProject
from udo import default_settings


def query_project_code_list_by_username(username: str):
    if username in default_settings.ADMIN:
        project_list = UdoProject.query.all()
        return [x.project_code for x in project_list]
    project_user_list = UdoProjectUser.query.filter(UdoProjectUser.username == username).all()
    project_code_list = []
    if project_user_list:
        for project_user in project_user_list:
            project_code_list.append(project_user.project_code)
    return project_code_list

