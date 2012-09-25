# Copyright 2012 Anton Beloglazov
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" The functions from this module are shared by other components.
"""

from contracts import contract
from neat.contracts_extra import *

import os
import time

from neat.config import *
from neat.db_utils import *

import logging
log = logging.getLogger(__name__)


@contract
def start(init_state, execute, config, time_interval, iterations=-1):
    """ Start the processing loop.

    :param init_state: A function accepting a config and
                       returning a state dictionary.
     :type init_state: function

    :param execute: A function performing the processing at each iteration.
     :type execute: function

    :param config: A config dictionary.
     :type config: dict(str: *)

    :param time_interval: The time interval to wait between iterations.
     :type time_interval: int

    :param iterations: The number of iterations to perform, -1 for infinite.
     :type iterations: int

    :return: The final state.
     :rtype: dict(str: *)
    """
    state = init_state(config)

    if iterations == -1:
        while True:
            state = execute(config, state)
            time.sleep(time_interval)
    else:
        for _ in xrange(iterations):
            state = execute(config, state)
            time.sleep(time_interval)

    return state


@contract
def build_local_vm_path(local_data_directory):
    """ Build the path to the local VM data directory.

    :param local_data_directory: The base local data path.
     :type local_data_directory: str

    :return: The path to the local VM data directory.
     :rtype: str
    """
    return os.path.join(local_data_directory, 'vms')


@contract
def physical_cpu_count(vir_connection):
    """ Get the number of physical CPUs using libvirt.

    :param vir_connection: A libvirt connection object.
     :type vir_connection: virConnect

    :return: The number of physical CPUs.
     :rtype: int
    """
    return vir_connection.getInfo()[2]


@contract
def physical_cpu_mhz(vir_connection):
    """ Get the CPU frequency in MHz using libvirt.

    :param vir_connection: A libvirt connection object.
     :type vir_connection: virConnect

    :return: The CPU frequency in MHz.
     :rtype: int
    """
    return vir_connection.getInfo()[1]


@contract
def physical_cpu_mhz_total(vir_connection):
    """ Get the sum of the core CPU frequencies in MHz using libvirt.

    :param vir_connection: A libvirt connection object.
     :type vir_connection: virConnect

    :return: The total CPU frequency in MHz.
     :rtype: int
    """
    return physical_cpu_count(vir_connection) * \
        physical_cpu_mhz(vir_connection)


@contract
def frange(start, end, step):
    """ A range generator for floats.

    :param start: The starting value.
     :type start: number

    :param end: The end value.
     :type end: number

    :param step: The step.
     :type step: number
    """
    while start <= end:
        yield start
        start += step


@contract
def init_logging(log_directory, log_file, log_level):
    """ Initialize the logging system.

    :param log_directory: The directory to store log files.
     :type log_directory: str

    :param log_file: The file name to store log messages.
     :type log_file: str

    :param log_level: The level of emitted log messages.
     :type log_level: int

    :return: Whether the logging system has been initialized.
     :rtype: bool
    """
    if log_level == 0:
        logging.disable(logging.CRITICAL)
        return True

    if not os.access(log_file, os.F_OK):
        if not os.access(log_directory, os.F_OK):
            os.makedirs(log_directory)
        elif not os.access(log_directory, os.W_OK):
            raise IOError(
                'Cannot write to the log directory: ' + log_directory)
    elif not os.access(log_file, os.W_OK):
        raise IOError('Cannot write to the log file: ' + log_file)

    if log_level == 3:
        level = logging.DEBUG
    elif log_level == 2:
        level = logging.INFO
    else:
        level = logging.WARNING

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(name)s %(message)s',
        filename=os.path.join(log_directory, log_file),
        level=level)
    return True
