# This file is part of sner4 project governed by MIT license, see the LICENSE.txt file.
"""
scheduler job views
"""

import json
import os

from datatables import ColumnDT, DataTables
from flask import redirect, render_template, request, Response, url_for
from sqlalchemy import literal_column
from sqlalchemy_filters import apply_filters

from sner.server import db
from sner.server.auth.core import role_required
from sner.server.forms import ButtonForm
from sner.server.scheduler.models import Job, Queue
from sner.server.scheduler.views import scheduler_blueprint
from sner.server.sqlafilter import filter_parser
from sner.server.utils import SnerJSONEncoder


def job_delete(job):
    """job delete; used by controller and respective command"""

    if os.path.exists(job.output_abspath):
        os.remove(job.output_abspath)
    db.session.delete(job)
    db.session.commit()


@scheduler_blueprint.route('/job/list')
@role_required('operator')
def job_list_route():
    """list jobs"""

    return render_template('scheduler/job/list.html')


@scheduler_blueprint.route('/job/list.json', methods=['GET', 'POST'])
@role_required('operator')
def job_list_json_route():
    """list jobs, data endpoint"""

    columns = [
        ColumnDT(Job.id, mData='id'),
        ColumnDT(Queue.id, mData='queue_id'),
        ColumnDT(Queue.name, mData='queue_name'),
        ColumnDT(Job.assignment, mData='assignment'),
        ColumnDT(Job.retval, mData='retval'),
        ColumnDT(Job.time_start, mData='time_start'),
        ColumnDT(Job.time_end, mData='time_end'),
        ColumnDT((Job.time_end-Job.time_start), mData='time_taken'),
        ColumnDT(literal_column('1'), mData='_buttons', search_method='none', global_search=False)
    ]
    query = db.session.query().select_from(Job).outerjoin(Queue)
    if 'filter' in request.values:
        query = apply_filters(query, filter_parser.parse(request.values.get('filter')), do_auto_join=False)

    jobs = DataTables(request.values.to_dict(), query, columns).output_result()
    return Response(json.dumps(jobs, cls=SnerJSONEncoder), mimetype='application/json')


@scheduler_blueprint.route('/job/delete/<job_id>', methods=['GET', 'POST'])
@role_required('operator')
def job_delete_route(job_id):
    """delete job"""

    form = ButtonForm()

    if form.validate_on_submit():
        job_delete(Job.query.get(job_id))
        return redirect(url_for('scheduler.job_list_route'))

    return render_template('button-delete.html', form=form)
