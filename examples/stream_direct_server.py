#!/usr/bin/env python3.4
#
# Copyright (c) 2013-2015 by Ron Frederick <ronf@timeheart.net>.
# All rights reserved.
#
# This program and the accompanying materials are made available under
# the terms of the Eclipse Public License v1.0 which accompanies this
# distribution and is available at:
#
#     http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#     Ron Frederick - initial implementation, API, and documentation

# To run this program, the file ``ssh_host_key`` must exist with an SSH
# private key in it to use as a server host key. An SSH host certificate
# can optionally be provided in the file ``ssh_host_key-cert.pub``.
#
# The file ``ssh_user_ca`` must exist with a cert-authority entry of
# the certificate authority which can sign valid client certificates.

import asyncio, asyncssh, sys

@asyncio.coroutine
def handle_connection(reader, writer):
    while not reader.at_eof():
        data = yield from reader.read(8192)

        try:
            writer.write(data)
        except BrokenPipeError:
            break

    writer.close()

class MySSHServer(asyncssh.SSHServer):
    def connection_requested(self, dest_host, dest_port, orig_host, orig_port):
        if dest_port == 7:
            return handle_connection
        else:
            raise asyncssh.ChannelOpenError(
                      asyncssh.OPEN_ADMINISTRATIVELY_PROHIBITED,
                      'Only echo connections allowed')

@asyncio.coroutine
def start_server():
    yield from asyncssh.create_server(MySSHServer, '', 8022,
                                      server_host_keys=['ssh_host_key'],
                                      authorized_client_keys='ssh_user_ca')

loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(start_server())
except (OSError, asyncssh.Error) as exc:
    sys.exit('SSH server failed: ' + str(exc))

loop.run_forever()
