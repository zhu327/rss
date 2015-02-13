import threading
from tornado import template, web
import jinja2


class TTemplate(object):
    def __init__(self, template_instance):
        self.template_instance = template_instance

    def generate(self, **kwargs):
        return self.template_instance.render(**kwargs)


class JinjaLoader(template.BaseLoader):
    def __init__(self, root_directory, **kwargs):
        self.jinja_env = \
            jinja2.Environment(loader=jinja2.FileSystemLoader(root_directory),
                               **kwargs)
        self.templates = {}
        self.lock = threading.RLock()

    def resolve_path(self, name, parent_path=None):
        return name

    def _create_template(self, name):
        template_instance = TTemplate(self.jinja_env.get_template(name))
        return template_instance
