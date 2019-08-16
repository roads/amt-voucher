# -*- coding: utf-8 -*-
# Copyright 2019 Brett D. Roads. All Rights Reserved.
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
# ==============================================================================

"""Create a HIT on Amazon Mechanical Turk (AMT).

Arguments:
    See argument parser or execute `python create_hit.py -h`.

Example usage:
    python create_hit.py hit_config.json "roads" --live

"""

import argparse
import datetime
import json
from pathlib import Path
from pprint import pprint

import boto3


def main(fp_hit_config, aws_profile, n_assignment, is_live, fp_app, verbose):
    """Execute script."""
    # Create application folders if necessary.
    fp_logs = fp_app / Path('logs', aws_profile)
    if not fp_logs.exists():
        fp_logs.mkdir(parents=True)

    # Load AMT configuration file.
    with open(fp_hit_config) as f:
        hit_cfg = json.load(f)
    if verbose > 0:
        pprint(hit_cfg)

    ymd_str = datetime.datetime.today().strftime('%Y-%m-%d')

    if is_live:
        # Create a live HIT.
        print_warnings(hit_cfg, n_assignment, is_live)
        print("Are you sure you want to create the HIT (yes/no)?")
        r = input()
        if (r == 'yes') or (r == 'y'):
            hitId = create_hit(hit_cfg, n_assignment, is_live, aws_profile)
            print("    Created live HIT {0}".format(hitId))
            with open(fp_logs / Path('hit_live.txt'), 'a') as f:
                f.write(
                    "{0}, {1}, {2}\n".format(hitId, ymd_str, fp_hit_config)
                )

        else:
            print("    Did not create HIT")
    else:
        # Create a HIT on AMT's sandbox site.
        hitId = create_hit(hit_cfg, n_assignment, is_live, aws_profile)

        print("    Created sandbox HIT {0}".format(hitId))
        with open(fp_logs / Path('hit_sandbox.txt'), 'a') as f:
            f.write(
                "{0}, {1}, {2}\n".format(hitId, ymd_str, fp_hit_config)
            )


def create_hit(hit_cfg, n_assignment, is_live, aws_profile):
    """Create HIT."""
    # Start client.
    session = boto3.Session(profile_name=aws_profile)
    # Any clients created from this session will use credentials
    # from the [<aws_profile>] section of ~/.aws/credentials.

    endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
    if is_live:
        endpoint_url = 'https://mturk-requester.us-east-1.amazonaws.com'
    amt_client = session.client('mturk', endpoint_url=endpoint_url)

    # Create question XML.
    question_xml = external_question_xml(hit_cfg['QuestionUrl'])

    response = amt_client.create_hit(
        MaxAssignments=n_assignment,
        # AutoApprovalDelayInSeconds=123,
        LifetimeInSeconds=hit_cfg['LifetimeInSeconds'],
        AssignmentDurationInSeconds=hit_cfg['AssignmentDurationInSeconds'],
        Reward=hit_cfg['Reward'],
        Title=hit_cfg['Title'],
        Keywords=hit_cfg['Keywords'],
        Description=hit_cfg['Description'],
        Question=question_xml,
        # RequesterAnnotation='string',
        QualificationRequirements=hit_cfg['QualificationRequirements'],
        # UniqueRequestToken='string',
        # AssignmentReviewPolicy={
        #     'PolicyName': 'string',
        #     'Parameters': [
        #         {
        #             'Key': 'string',
        #             'Values': [
        #                 'string',
        #             ],
        #             'MapEntries': [
        #                 {
        #                     'Key': 'string',
        #                     'Values': [
        #                         'string',
        #                     ]
        #                 },
        #             ]
        #         },
        #     ]
        # },
        # HITReviewPolicy={
        #     'PolicyName': 'string',
        #     'Parameters': [
        #         {
        #             'Key': 'string',
        #             'Values': [
        #                 'string',
        #             ],
        #             'MapEntries': [
        #                 {
        #                     'Key': 'string',
        #                     'Values': [
        #                         'string',
        #                     ]
        #                 },
        #             ]
        #         },
        #     ]
        # },
        # HITLayoutId='string',
        # HITLayoutParameters=[
        #     {
        #         'Name': 'string',
        #         'Value': 'string'
        #     },
        # ]
    )
    hitId = response['HIT']['HITId']
    return hitId


def print_warnings(hit_cfg, n_assignment, is_live):
    """Print relevant warnings."""
    if is_live:
        print(
            "    WARNING:  You are creating a live HIT that uses real "
            "money."
        )
        if n_assignment > 9:
            print(
                "    WARNING: AMT charges an additional 20%% fee "
                "for HITs with more than 9 assignments."
            )


def external_question_xml(question_url):
    """Return AMT-formatted XML for external question.

    See: https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/
    ApiReference_ExternalQuestionArticle.html
    """
    question_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<ExternalQuestion xmlns="http://mechanicalturk.amazonaws.com/'
        'AWSMechanicalTurkDataSchemas/2006-07-14/ExternalQuestion.xsd">'
        '<ExternalURL>{0}</ExternalURL>'
        '<FrameHeight>0</FrameHeight>'
        '</ExternalQuestion>'
    ).format(question_url)
    return question_xml


if __name__ == "__main__":
    # Parse arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "fp_hit_config", type=str,
        help="String indicating the path to the desired HIT configuration."
    )

    parser.add_argument(
        "aws_profile", type=str,
        help=(
            "String indicating AWS profile to use. Prfiles are assumed to be"
            "stored in a shared credentials file (~/.aws/credentials). For "
            " more details regarding the creation of profiles see https://"
            "boto3.amazonaws.com/v1/documentation/api/latest/guide/"
            "configuration.html."
        )
    )

    parser.add_argument(
        "-n", "--n_assignment", type=int, default=1,
        help="The maximum number of assignments."
    )

    parser.add_argument(
        '--live', dest='live', action='store_true',
        help=(
            "Deploys the HIT to the live AMT site. If flag is not used, the"
            " HIT is deployed to the AMT sandbox site."
        )
    )
    parser.set_defaults(live=False)

    parser.add_argument(
        "--fp_app", default=Path.home() / Path('.amt-voucher'),
        help=(
            "File path for application directory which holds configuration"
            " files and outputs."
        )
    )

    parser.add_argument(
        "-v", "--verbose", type=int, default=0,
        help="Increase output verbosity."
    )

    args = parser.parse_args()
    main(
        args.fp_hit_config, args.aws_profile, args.n_assignment, args.live,
        args.fp_app, args.verbose
    )
