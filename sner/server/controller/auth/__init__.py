"""authentication handling module"""

import flask_login
from flask import Blueprint, flash, redirect, render_template, url_for

from sner.server import login_manager
from sner.server.form.auth import LoginForm
from sner.server.model.auth import User

blueprint = Blueprint('auth', __name__)  # pylint: disable=invalid-name


@login_manager.user_loader
def user_loader(user_id):
    """flask_login user loader"""

    return User.query.filter(User.id == user_id).one_or_none()


@blueprint.route('/login', methods=['GET', 'POST'])
def login_route():
    """login route"""

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(User.username == form.username.data).one_or_none()
        if user and (user.password == form.password.data):
            flask_login.login_user(user)
            return redirect(url_for('auth.login_test_route'))

        flash('Bad credentials', 'error')

    return render_template('auth/login.html', form=form, form_url=url_for('auth.login_route'))


@blueprint.route('/logout')
def logout_route():
    """logout route"""

    flash('Logged out', 'info')
    return redirect(url_for('index_route'))


@blueprint.route('/login_test')
@flask_login.login_required
def login_test_route():
    """test login route"""

    return 'Logged in as: %s' % flask_login.current_user.username


@login_manager.unauthorized_handler
def unauthorized_handler():
    """unauthorized handler"""

    flash('Unauthorized', 'error')
    return redirect(url_for('index_route'))