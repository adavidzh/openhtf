# Copyright 2018 Google Inc. All Rights Reserved.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Simple OpenHTF test which launches the web GUI client."""

import openhtf as htf
from openhtf.util import conf

from openhtf.output.servers import station_server
from openhtf.output.web_gui import web_launcher
from openhtf.plugs import user_input
from openhtf.output.callbacks import json_factory

import os
import time
from pprint import pprint
import json

@htf.measures(htf.Measurement('hello_world_measurement'))
def hello_world_measurement_phase(test):
  test.logger.info('Hello world! Making a measurement is cool.')
  time.sleep(1)
  test.measurements.hello_world_measurement = 'Hello, this is a measurement result!'

def warning_exception_phase(test):
  test.logger.info("Throwing a RuntimeWarning would stop the testing.")
  time.sleep(1)
  pprint(test.test_record.phases)
  #raise RuntimeWarning('This might be worrisome')

def attach_and_fail_phase(test):
    time.sleep(5)
    test.logger.info("Let's attach a couple of things. return False at the end would stop the testing")

    test.attach(
        'test_attachment',
        'This is test attachment data.'.encode('utf-8')
    )
    test.attach_from_file(
        os.path.join(os.path.dirname(__file__),
        'example_attachment.txt')
    )
    test_attachment = test.get_attachment('test_attachment')
    test.logger.info(test_attachment.data)
    #return False

def final_phase(test):
    time.sleep(5)
    test.logger.info('Simple final phase that logs a warning.')
    test.logger.warning('This is the final phase warning!')

if __name__ == '__main__':
  conf.load(station_server_port='4444')
  with station_server.StationServer() as server:
    # web_launcher.launch('http://localhost:4444')
    for i in range(3):
        test = htf.Test(
            hello_world_measurement_phase,
            warning_exception_phase,
            attach_and_fail_phase,
            final_phase
        )
        test.add_output_callbacks(server.publish_final_state)
        test.add_output_callbacks(
          json_factory.OutputToJSON('./frontend_example_thing.report.json', indent=2))
        test.execute(test_start=user_input.prompt_for_test_start())
