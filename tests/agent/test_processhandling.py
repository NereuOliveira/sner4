# This file is part of sner4 project governed by MIT license, see the LICENSE.txt file.
"""
agents process handling
"""

import json
import multiprocessing
import os
from http import HTTPStatus
from time import sleep
from uuid import uuid4

from werkzeug.wrappers import Response

from sner.agent import main as agent_main


def test_terminate_with_assignment(tmpworkdir, cleanup_markedprocess, test_longrun_a):  # pylint: disable=unused-argument
    """
    Agent external process handling test. Even thou the test uses nmap module, the point is to test sner.agent.modules.Base _terminate helper.
    """

    proc_agent = multiprocessing.Process(target=agent_main, args=(['--assignment', json.dumps(test_longrun_a), '--debug'],))
    proc_agent.start()
    sleep(1)
    assert proc_agent.pid
    assert proc_agent.is_alive()

    agent_main(['--terminate', str(proc_agent.pid)])
    proc_agent.join(3)
    assert not proc_agent.is_alive()
    assert 'MARKEDPROCESS' not in os.popen('ps -f').read()


def test_terminate_with_liveserver(tmpworkdir, live_server, apikey, cleanup_markedprocess, test_longrun_target):  # noqa: ignore=E501  pylint: disable=unused-argument,redefined-outer-name
    """
    Agent external process handling test. Even thou the test uses nmap module, the point is to test sner.agent.modules.Base _terminate helper.
    """

    proc_agent = multiprocessing.Process(
        target=agent_main,
        args=(['--server', live_server.url(), '--apikey', apikey, '--debug', '--queue', str(test_longrun_target.queue_id), '--oneshot'],))
    proc_agent.start()
    sleep(1)
    assert proc_agent.pid
    assert proc_agent.is_alive()

    agent_main(['--terminate', str(proc_agent.pid)])
    proc_agent.join(3)
    assert not proc_agent.is_alive()
    assert 'MARKEDPROCESS' not in os.popen('ps -f').read()


class SimpleServer():
    """external server for agent comm tests"""

    def __init__(self, server):
        self.server = server
        self.url = self.server.url_for('/')[:-1]
        self.server.expect_request('/api/v1/scheduler/job/assign').respond_with_handler(self.handler_assign)
        self.server.expect_request('/api/v1/scheduler/job/output').respond_with_handler(self.handler_output)

    @staticmethod
    def handler_assign(request):
        """handle assign request"""
        if request.headers.get('Authorization') != 'Apikey dummy':
            return Response('Unauthorized', status=HTTPStatus.UNAUTHORIZED)
        return Response(json.dumps({'id': str(uuid4()), 'module': 'dummy', 'params': '', 'targets': []}))

    @staticmethod
    def handler_output(request):
        """handle output request"""
        if request.headers.get('Authorization') != 'Apikey dummy':
            return Response('Unauthorized', status=HTTPStatus.UNAUTHORIZED)
        return Response('', status=HTTPStatus.OK)


def test_shutdown(tmpworkdir, httpserver):  # pylint: disable=unused-argument,redefined-outer-name
    """test no-work, continuous job assignment and shutdown signal handling"""

    sserver = SimpleServer(httpserver)

    proc_agent = multiprocessing.Process(
        target=agent_main,
        args=(['--server', sserver.url, '--apikey', 'dummy', '--debug'],))
    proc_agent.start()
    sleep(1)
    assert proc_agent.is_alive()

    agent_main(['--shutdown', str(proc_agent.pid)])
    proc_agent.join(1)
    assert not proc_agent.is_alive()
