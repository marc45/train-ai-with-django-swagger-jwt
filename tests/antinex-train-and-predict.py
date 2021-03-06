#!/usr/bin/env python

import os
import sys
import json
import argparse
import requests
from antinex_utils.log.setup_logging import build_colorized_logger
from antinex_utils.utils import ppj


name = "antinex-train-and-predict"
log = build_colorized_logger(name=name)

"""
make sure to clone the antinex-datasets repo locally:

git clone https://github.com/jay-johnson/antinex-datasets.git \
    /opt/antinex-datasets
"""

parser = argparse.ArgumentParser(description="Train a Deep Neural Network")
parser.add_argument(
    "-f",
    help="file to use default ./django-antinex.json",
    required=False,
    dest="data_file")
args = parser.parse_args()

test_data_file = os.getenv(
    "TEST_DATA",
    "./django-antinex.json")
if args.data_file:
    if os.path.exists(args.data_file):
        test_data_file = args.data_file
    else:
        log.error("Missing data_file: -f {}".format(
            args.data_file))
        sys.exit(1)
# end of assigning data file

url = os.getenv(
    "ANTINEX_URL",
    "http://localhost:8080")
username = os.getenv(
    "API_USER",
    "root")
password = os.getenv(
    "API_PASS",
    "123321")

if not os.path.exists(test_data_file):
    log.error(("Failed to find test_data_file={}")
              .format(test_data_file))
    sys.exit(1)
# end of checking the path to the test json file

test_data = json.loads(open(test_data_file, "r").read())

auth_url = "{}/api-token-auth/".format(url)
resource_url = "{}/ml/".format(url)
use_headers = {
    "Content-type": "application/json"
}
login_data = {
    "username": username,
    "password": password
}

# Login as the user:
log.info("Logging in user url={}".format(auth_url))
post_response = requests.post(auth_url,
                              data=json.dumps(login_data),
                              headers=use_headers)

user_token = ""
if post_response.status_code == 200:
    user_token = json.loads(post_response.text)["token"]

if user_token == "":
    log.error(("Failed logging in as user={} - stopping"
               "post_response={}")
              .format(username,
                      post_response.text))
    sys.exit(1)
else:
    log.info(("logged in user={} token={}")
             .format(username,
                     user_token))
# end if/else

log.info("building post data")

use_headers = {
    "Content-type": "application/json",
    "Authorization": "JWT {}".format(user_token)
}

log.info(("Running ML Job url={} "
          "test_data={}")
         .format(resource_url,
                 test_data))
post_response = requests.post(resource_url,
                              data=json.dumps(test_data),
                              headers=use_headers)

if post_response.status_code != 201 \
   and post_response.status_code != 200:
    log.error(("Failed with Post response status={} reason={}")
              .format(post_response.status_code,
                      post_response.reason))
    log.error("Details:\n{}".format(post_response.text))
    sys.exit(1)
else:
    log.info(("SUCCESS - Post Response status={} reason={}")
             .format(post_response.status_code,
                     post_response.reason))

    as_json = True
    record = {}
    if as_json:
        record = json.loads(post_response.text)
        log.info(ppj(record))
# end of post for running an ML Job

sys.exit(0)
