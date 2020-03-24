# This file is part of sner4 project governed by MIT license, see the LICENSE.txt file.
"""
sner planner module
"""

import click
from flask.cli import with_appcontext

from sner.server.command.scheduler import enumerate_network
from sner.server.model.scheduler import Queue

TARGET_NETWORKS = [
    '78.128.214.0/26',
#    '195.113.0.0/16'
]
SERVICE_DISCOVERY_QUEUE='sner_011 top10000 ack scan.main'
SERVICE_VERSION_SCANE_QUEUE='sner_020 inet version scan basic.main'


@click.group(name='planner', help='sner.server planner management')
def planner_command():
    """planner commands click group/container"""


@planner_command.command(name='run', help='run planner daemon')
@with_appcontext
def planner_run():

    # SETUP
    # ensure service discovery task
    # ensure service discovery queue
    # ensure service version scan task
    # ensure service version scan queue

    # EXECUTION

    # enqueue all enumerated targets
    targets = []
    for target in TARGET_NETWORKS:
        targets.extend(enumerate_network(target))

    disco_queue = Queue.query.filter(Queue.ident == SERVICE_DISCOVERY_QUEUE).one()

    # monitor queue/job
        # for every completed job in SD queue
            # parse services from output, enqueue to SV queue
            # delete completed job

        # for every completed job in SV queue
            # import output to storage
            # delete completed job

    # cleanup storage
