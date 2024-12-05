from pathlib import Path
from jinja2 import Environment

class Project:
    HOST_PATH = '/home/fernando/apps/'
    NGINX_PATH = '/etc/nginx/sites-enabled'
    NGINX_TEMPLATE = '''
server {
    listen 80;
    server_name {{ project_name }}.test;
    root {{ project_path }}/public;

    index index.php index.html index.htm;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        include fastcgi_params;
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    }

    error_log /var/log/nginx/tracker-error.log;
    access_log /var/log/nginx/tracker-access.log;
}
    '''

    def __init__(self, path):
        self.path = path
        self.jinja2_template = Environment()

    def has_nginx_config(self):
        directory_path = Path(self.NGINX_PATH)

        for item in directory_path.iterdir():
            if item.is_file() and item.name == self.path:
                return True

        return False

    def add_entry_to_hosts(self):
        hosts = Path('/etc/hosts')

        with hosts.open("a") as f:
            f.write("127.0.0.1    {}.test".format(self.path))

    def get_template(self):
        template = self.jinja2_template.from_string(self.NGINX_TEMPLATE)
        return template.render({
            "project_name": self.path,
            "project_path": "{}{}".format(self.HOST_PATH, self.path)
        })

    def create_nginx_config(self):
        template = self.get_template()
        file_name = "{}/{}".format(self.NGINX_PATH, self.path)
        new_file = Path(file_name)
        new_file.touch()
        new_file.write_text(template)

        self.add_entry_to_hosts()


APPS_DIR = '/home/fernando/apps'

def get_all_directories(path):
    path_obj = Path(path)
    if path_obj.is_dir():
        directories = [item for item in path_obj.iterdir() if item.is_dir()]
        return directories
    else:
        raise ValueError(f"The path {path} is not a directory.")

try:
    directories = get_all_directories(APPS_DIR)
    for directory in directories:
        project = Project(directory.name)

        if not project.has_nginx_config():
            project.create_nginx_config()
except ValueError as e:
    print(e)