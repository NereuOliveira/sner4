"""authentication handling module"""

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_user, logout_user

from sner.server import login_manager
from sner.server.form.auth import LoginForm
from sner.server.model.auth import User

blueprint = Blueprint('auth', __name__)  # pylint: disable=invalid-name

import sner.server.controller.auth.user  # noqa: E402,F401  pylint: disable=wrong-import-position


@login_manager.user_loader
def user_loader(user_id):
    """flask_login user loader"""

    return User.query.filter(User.id == user_id).one_or_none()


@blueprint.route('/login', methods=['GET', 'POST'])
def login_route():
    """login route"""

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(User.active, User.username == form.username.data).one_or_none()
        if user and user.compare_password(form.password.data):
            login_user(user)
            return redirect(url_for('index_route'))

        flash('Invalid credentials', 'error')

    return render_template('auth/login.html', form=form, form_url=url_for('auth.login_route'))


@blueprint.route('/logout')
def logout_route():
    """logout route"""

    logout_user()
    flash('Logged out', 'info')
    return redirect(url_for('index_route'))


@login_manager.unauthorized_handler
def unauthorized_handler():
    """unauthorized handler; not logged in"""

    flash('Not logged in', 'warning')
    return redirect(url_for('auth.login_route'))
