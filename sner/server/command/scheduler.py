# This file is part of sner4 project governed by MIT license, see the LICENSE.txt file.
"""
scheduler commands
"""

import sys
from ipaddress import ip_address, ip_network, summarize_address_range

import click
from flask import current_app
from flask.cli import with_appcontext

from sner.server import db
from sner.server.controller.scheduler.job import job_delete
from sner.server.model.scheduler import Job, Queue, Target


def queuebyx(queue_ident):
    """get queue by id or name"""

    if queue_ident.isnumeric():
        return Queue.query.get(int(queue_ident))
    return Queue.query.filter(Queue.ident == queue_ident).one_or_none()


def enumerate_network(arg):
    """enumerate ip address range"""

    network = ip_network(arg)
    data = list(network.hosts())
    if network.prefixlen == network.max_prefixlen:
        data.append(network.network_address)
    return data


def enqueue(queue, targets):
    """enqueue targets to queue"""

    enqueued = []
    for target in targets:
        enqueued.append({'target': target, 'queue_id': queue.id})
    db.session.bulk_insert_mappings(Target, enqueued)
    db.session.commit()


@click.group(name='scheduler', help='sner.server scheduler management')
def scheduler_command():
    """scheduler commands click group/container"""


@scheduler_command.command(name='enumips', help='enumerate ip address range')
@click.argument('targets', nargs=-1)
@click.option('--file', type=click.File('r'))
def enumips(targets, **kwargs):
    """enumerate ip address range"""

    targets = list(targets)
    if kwargs['file']:
        targets += kwargs['file'].read().splitlines()
    for target in targets:
        print('\n'.join(enumerate_network(target)))


@scheduler_command.command(name='rangetocidr', help='convert range specified addr space to series of cidr')
@click.argument('start')
@click.argument('end')
def rangetocidr(start, end):
    """summarize net rage into cidrs"""

    for tmp in summarize_address_range(ip_address(start), ip_address(end)):
        print(tmp)


@scheduler_command.command(name='queue-enqueue', help='add targets to queue')
@click.argument('queue_ident')
@click.argument('argtargets', nargs=-1)
@click.option('--file', type=click.File('r'))
@with_appcontext
def queue_enqueue(queue_ident, argtargets, **kwargs):
    """enqueue targets to queue"""

    queue = queuebyx(queue_ident)
    if not queue:
        current_app.logger.error('no such queue')
        sys.exit(1)

    argtargets = list(argtargets)
    if kwargs['file']:
        argtargets.extend(kwargs['file'].read().splitlines())
    argtargets = list(map(lambda x: x.strip(), argtargets))

    enqueue(queue, argtargets)
    sys.exit(0)


@scheduler_command.command(name='queue-flush', help='flush all targets from queue')
@click.argument('queue_id')
@with_appcontext
def queue_flush(queue_id):
    """flush targets from queue"""

    queue = queuebyx(queue_id)
    if not queue:
        current_app.logger.error('no such queue')
        sys.exit(1)

    db.session.query(Target).filter(Target.queue_id == queue.id).delete()
    db.session.commit()
    sys.exit(0)


@scheduler_command.command(name='queue-prune', help='delete all associated jobs')
@click.argument('queue_id')
@with_appcontext
def queue_prune(queue_id):
    """delete all jobs associated with queue"""

    queue = queuebyx(queue_id)
    if not queue:
        current_app.logger.error('no such queue')
        sys.exit(1)

    for job in Job.query.filter(Job.queue_id == queue.id).all():
        job_delete(job)
    sys.exit(0)
