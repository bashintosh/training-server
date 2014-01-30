#!/usr/bin/env python

# Copyright (c) 2014 Martin Abente Lahaye. - tch@sugarlabs.org
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

import os
from ConfigParser import ConfigParser

from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado.web import Application
from tornado.netutil import bind_sockets
from tornado.process import fork_processes

from training.datastore import DataStore
from training.handlers import ReportHandler
from training.handlers import ConfirmationHandler


def main():
    script_path = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(script_path, 'etc/training.cfg')
    confirm_path = os.path.join(script_path, 'data/confirmation.text')

    config = ConfigParser()
    config.read(config_path)

    sockets = bind_sockets(config.get('server', 'port'))
    fork_processes(config.getint('server', 'instances'))

    datastore = DataStore(config.get('database', 'host'),
                          config.getint('database', 'port'),
                          config.get('database', 'username'),
                          config.get('database', 'password'),
                          config.get('database', 'database'))

    with open(confirm_path) as file:
        message = file.read()

    params_report = {'datastore': datastore,
                     'api_key': config.get('server', 'api_key')}
    params_confirm = {'datastore': datastore,
                      'message': message}

    app = Application([(r"/training/report",
                        ReportHandler, params_report),
                       (r"/training/confirm/(.*)",
                        ConfirmationHandler, params_confirm)])

    server = HTTPServer(app,
                        no_keep_alive=config.get('server', 'no_keep_alive'),
                        ssl_options={
                            'certfile': config.get('server', 'certfile'),
                            'keyfile': config.get('server', 'keyfile')})

    server.add_sockets(sockets)
    IOLoop.instance().start()

if __name__ == "__main__":
    main()
