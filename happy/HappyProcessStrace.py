#!/usr/bin/env python3

#
#    Copyright (c) 2016-2017 Nest Labs, Inc.
#    All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#

##
#    @file
#       Implements HappyProcessStrace class that returns an strace of
#       a process running within virtual node.
#
#       Process runs a command in a virtual node, which itself
#       is a logical representation of a network namespace.
#

from __future__ import absolute_import
import os
import sys

from happy.ReturnMsg import ReturnMsg
from happy.Utils import *
from happy.HappyNode import HappyNode

options = {}
options["quiet"] = False
options["node_id"] = None
options["tag"] = None


def option():
    return options.copy()


class HappyProcessStrace(HappyNode):
    """
    Displays the output of a process strace.

    happy-process-strace [-h --help] [-q --quiet] [-i --id <NODE_NAME>]
                         [-t --tag <DAEMON_NAME>]

        -i --id     Optional. Node on which the process is running. Find using
                    happy-node-list or happy-state.
        -t --tag    Required. Name of the process.

    Example:
    $ happy-process-strace ThreadNode ContinuousPing
        Displays the output of the strace for the ContinuousPing process
        on the ThreadNode node.

    return:
        0    success
        1    fail
    """

    def __init__(self, opts=options):
        HappyNode.__init__(self)

        self.quiet = opts["quiet"]
        self.node_id = opts["node_id"]
        self.tag = opts["tag"]
        self.process_strace = None

    def __pre_check(self):
        # Check if the new process is given
        if not self.tag:
            emsg = "Missing name of the process to retrieve strace from."
            self.logger.error("[localhost] HappyProcessStrace: %s" % (emsg))
            self.RaiseError()

    def __process_strace(self):
        fout = self.getNodeProcessStraceFile(self.tag, self.node_id)

        if not os.path.exists(fout):
            # Delay read in case of race condition
            delayExecution(0.5)

        try:
            with open(fout, 'r') as pout:
                self.process_strace = pout.read()

        except IOError as e:
            emsg = "Problem with %s: " % (fout)
            emsg += "I/O error({0}): {1}".format(e.errno, e.strerror)
            self.logger.error("[localhost] HappyProcessStrace: %s" % emsg)
            self.RaiseError(fout + ": " + e.strerror)

        except Exception:
            emsg = "Failed to open process strace file: %s." % (fout)
            self.logger.error("[localhost] HappyProcessStrace: %s" % emsg)
            self.RaiseError(emsg)

    def run(self):
        self.__pre_check()

        self.__process_strace()

        return ReturnMsg(0, self.process_strace)
