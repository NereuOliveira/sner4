# This file is part of sner4 project governed by MIT license, see the LICENSE.txt file.
"""
controller storage main module
"""

from http import HTTPStatus

from flask import Blueprint, jsonify, render_template

from sner.server import db
from sner.server.form.storage import AnnotateForm, TagMultiidForm
from sner.server.model.storage import Host, Service


blueprint = Blueprint('storage', __name__)  # pylint: disable=invalid-name


def get_related_models(model_name, model_id):
    """get related host/service to bind vuln/note"""

    host, service = None, None
    if model_name == 'host':
        host = Host.query.get(model_id)
    elif model_name == 'service':
        service = Service.query.get(model_id)
        host = service.host
    return host, service


def annotate_model(model, model_id):
    """annotate model route"""

    model = model.query.get(model_id)
    form = AnnotateForm(obj=model)

    if form.validate_on_submit():
        form.populate_obj(model)
        db.session.commit()
        return '', HTTPStatus.OK

    return render_template('storage/annotate.html', form=form)


def tag_model_multiid(model_class):
    """tag model by id"""

    form = TagMultiidForm()
    if form.validate_on_submit():
        tag = form.tag.data
        for item in model_class.query.filter(model_class.id.in_([tmp.data for tmp in form.ids.entries])).all():
            # full assignment must be used for sqla to realize the change
            if form.action.data == 'set':
                item.tags = list(set((item.tags or []) + [tag]))
            if form.action.data == 'unset':
                item.tags = [x for x in item.tags if x != tag]
        db.session.commit()
        return '', HTTPStatus.OK

    return jsonify({'title': 'Invalid form submitted.'}), HTTPStatus.BAD_REQUEST


import sner.server.controller.storage.host  # noqa: E402  pylint: disable=wrong-import-position
import sner.server.controller.storage.service  # noqa: E402  pylint: disable=wrong-import-position
import sner.server.controller.storage.note  # noqa: E402  pylint: disable=wrong-import-position
import sner.server.controller.storage.vuln  # noqa: E402,F401  pylint: disable=wrong-import-position
