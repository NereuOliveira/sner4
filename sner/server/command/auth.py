"""auth commands"""

import sys

import click
from flask import current_app
from flask.cli import with_appcontext

from sner.server import db
from sner.server.password_supervisor import PasswordSupervisor
from sner.server.model.auth import User


@click.group(name='auth', help='sner.server auth management')
def auth_command():
    """auth commands click group/container"""


@auth_command.command(name='passwordreset', help='password reset')
@click.argument('username')
@with_appcontext
def passwordreset(username):
    """reset password for username"""

    user = User.query.filter(User.username == username).one_or_none()
    if not user:
        current_app.logger.error('no such queue')
        sys.exit(1)

    tmp_password = PasswordSupervisor().generate()
    user.password = tmp_password
    db.session.commit()
    current_app.logger.info('password reset "%s:%s"' % (user.username, tmp_password))
