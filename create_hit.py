"""Create a HIT on Amazon Mechanical Turk (AMT).

Arguments:
    fp_hit_config - The filepath to the AMT HIT configuration file.
    live (optional) - Boolean indicating if the HIT should be
        deployed to the live site. The default is false, which
        deploys the HIT to the sandbox site.

Example usage:
    python create_hit.py projects/e001/hit_config.json "mozer" -l True

"""
import os
import sys
import json
import argparse
from pprint import pprint

import boto3


def main(fp_hit_config, aws_profile, is_live, verbose):
    """Create HIT."""
    # Load AMT configuration file.
    with open(fp_hit_config) as f:
        hit_cfg = json.load(f)
    if verbose > 0:
        pprint(hit_cfg)

    if is_live:
        # Create a live HIT.
        print_warnings(hit_cfg, is_live)
        print("Are you sure you want to create the HIT (yes/no)?")
        r = input()
        if (r == 'yes') or (r == 'y'):
            hitId = create_hit(hit_cfg, is_live, aws_profile)
            print("    Created live HIT {0}".format(hitId))
            with open(os.path.join('records', 'hitid.txt'), 'a') as f:
                f.write("{0}, {1}\n".format(hitId, fp_hit_config))

        else:
            print("    Did not create HIT")
    else:
        # Create a HIT on AMT's sandbox site.
        hitId = create_hit(hit_cfg, is_live, aws_profile)

        print("    Created sandbox HIT {0}".format(hitId))
        with open(os.path.join('records', 'hitid_sandbox.txt'), 'a') as f:
            f.write("{0}, {1}\n".format(hitId, fp_hit_config))


def create_hit(hit_cfg, is_live, aws_profile):
    """Create HIT."""
    # Start client.
    session = boto3.Session(profile_name=aws_profile)
    # Any clients created from this session will use credentials
    # from the [<aws_profile>] section of ~/.aws/credentials.

    endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
    if is_live:
        endpoint_url = 'https://mturk-requester.us-east-1.amazonaws.com'
    # amt_client = boto3.client('mturk', endpoint_url=endpoint_url)
    amt_client = session.client('mturk', endpoint_url=endpoint_url)

    # Create question XML.
    question_xml = external_question_xml(hit_cfg['question_url'])

    response = amt_client.create_hit(
        MaxAssignments=hit_cfg['max_assignments'],
        # AutoApprovalDelayInSeconds=123,
        LifetimeInSeconds=hit_cfg['hit_lifetime_s'],
        AssignmentDurationInSeconds=hit_cfg['assignment_duration_s'],
        Reward=hit_cfg['hit_reward_dollar'],
        Title=hit_cfg['hit_title'],
        Keywords=hit_cfg['hit_keywords'],
        Description=hit_cfg['hit_description'],
        Question=question_xml,
        # RequesterAnnotation='string',
        QualificationRequirements=hit_cfg['quals'],
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


def print_warnings(hit_cfg, is_live):
    """Print relevant warnings."""
    if is_live:
        print(
            "    WARNING:  You are creating a live HIT that uses real ",
            "money."
        )
        if hit_cfg['max_assignments'] > 9:
            print(
                "    WARNING: AMT charges an additional 20%% fee ",
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


def str2bool(v):
    """Parse argument strings to a boolean value."""
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


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
        '--live', dest='live', action='store_true',
        help=(
            "Deploys the HIT to the live AMT site. If option is not specified"
            ", the HIT is deployed to the AMT sandbox site."
        )
    )
    parser.set_defaults(live=False)
    parser.add_argument(
        "-v", "--verbose", type=int, default=0,
        help="Increase output verbosity."
    )
    args = parser.parse_args()
    main(args.fp_hit_config, args.aws_profile, args.live, args.verbose)
