from werkzeug import abort


def templater(module, endpoint='tpl'):
    def func(app, path):
        print path
        module_name = app.module_names[module.import_name]
        path = '%s/%s' % (module_name, path)
        path = '/%s' % path.lstrip('/')
        print path
        template = app.get_template(path)
        if not template:
            path = '%s/index.html' % path.rstrip('/')
            template = app.get_template(path)
        if not template:
            abort(404)
        return template.render(app=app)

    module.add_route('/', endpoint, func, defaults={'path': 'index.html'})
    module.add_route('/<path:path>', endpoint, func)
