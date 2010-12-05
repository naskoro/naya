from naya.helpers import marker


@marker.route('/dashboard/')
def dashboard(app):
    return 'modular.admin.dashboard'
