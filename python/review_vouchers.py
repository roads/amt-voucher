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

"""Review and approve HITs with valid vouchers.

This script first checks if any HITs need review. If there are
reviewable HITs, then all associated assignments are reviewed. For each
completed assignment, the submitted voucher code (obtained from AMT
records) is compared to the hashed voucher code stored in the MySQL
database. If the codes match (after hashing), the the status_code of
the voucher is updated to "1" and the worker's assignment is approved.

Note:
    This script approves assignments solely on the basis of a valid
    voucher.

Arguments:
    aws_profile: he AWS profile to use.
    live (optional): Flag indicating if live HITs should be reviewed.
    verbose (optional): Sets the verbosity of output.

Example usage:
     python review_reviewable.py "mozer" -l True

"""

import argparse
import configparser
from pathlib import Path
import hashlib
import xml.etree.ElementTree as ET

import boto3
import mysql.connector

STATUS_VALID = 0
STATUS_REDEEMED = 1
STATUS_EXPIRED = 2


def main(profile, is_live, verbose):
    """Run script."""
    fp_mysql_cred = Path.home() / Path('.mysql/credentials')

    # AMT client.
    session = boto3.Session(profile_name=profile)

    endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
    if is_live:
        print("Mode: LIVE")
        endpoint_url = 'https://mturk-requester.us-east-1.amazonaws.com'
    else:
        print("Mode: SANDBOX")
    amt_client = session.client('mturk', endpoint_url=endpoint_url)

    # MySQL configuration.
    config = configparser.ConfigParser()
    config.read(fp_mysql_cred)
    mydb = mysql.connector.connect(
        host=config['amt_voucher']['servername'],
        user=config['amt_voucher']['username'],
        passwd=config['amt_voucher']['password'],
        database=config['amt_voucher']['database']
    )
    mycursor = mydb.cursor()

    resp = amt_client.list_reviewable_hits()
    n_hit = resp['NumResults']
    print('Reviewable HITs: {0}\n'.format(n_hit))
    for i_hit in range(n_hit):
        hit_id = resp['HITs'][i_hit]['HITId']
        inspect_hit(amt_client, mydb, mycursor, hit_id)


def inspect_hit(amt_client, mydb, mycursor, hit_id):
    """Inspect HIT for reviewable assignments."""
    resp = amt_client.get_hit(HITId=hit_id)
    print_hit_summary(resp)

    l = amt_client.list_assignments_for_hit(HITId=hit_id)
    n_assignment = l['NumResults']
    for i_assignment in range(n_assignment):
        amt_assignment_id = l['Assignments'][i_assignment]['AssignmentId']
        assignment_status = l['Assignments'][i_assignment]['AssignmentStatus']
        if assignment_status == 'Submitted':
            amt_assignment_answer = l['Assignments'][i_assignment]['Answer']
            (amt_worker_id, amt_voucher_code, amt_voucher_hash) = parse_amt_answer(amt_assignment_answer)
            print('    AMT Worker ID {0}'.format(amt_worker_id))

            (redeem_voucher, db_voucher_id) = verify_voucher_hash(
                mydb, mycursor, amt_worker_id, amt_assignment_id,
                amt_voucher_hash
            )
            if redeem_voucher:
                update_voucher_status(
                    mydb, mycursor, db_voucher_id, STATUS_REDEEMED
                )
                response = amt_client.approve_assignment(
                    AssignmentId=amt_assignment_id,
                    RequesterFeedback='Thank you for your work.'
                )
                http_status_code = response['ResponseMetadata']['HTTPStatusCode']
                if http_status_code == 200:
                    print('      Assignment sucessfully approved.')
                else:
                    print('      WARNING: Assignment may not have been approved successfully.')
    print('\n')


def print_hit_summary(resp):
    """Print HIT summary.

    The variable resp is the resturned result of the `get_hit` method.
    """
    hit_id = resp['HIT']['HITId']
    title = resp['HIT']['Title']
    hit_status = resp['HIT']['HITStatus']
    n_max = resp['HIT']['MaxAssignments']
    n_complete = resp['HIT']['NumberOfAssignmentsCompleted']
    n_pending = resp['HIT']['NumberOfAssignmentsPending']
    n_available = resp['HIT']['NumberOfAssignmentsAvailable']

    print('HIT ID: {0}'.format(hit_id))
    print('  Title: {0}'.format(title))
    print('  Status: {0}'.format(hit_status))
    print('  max | comp, pend, avail')
    print('  {0} | {1}, {2}, {3} '.format(
            n_max, n_complete, n_pending, n_available
        )
    )


def parse_amt_answer(amt_assignment_answer):
    """Parse XML-formatted answer."""
    # Clean XML.
    amt_assignment_answer = amt_assignment_answer.replace('<?xml version="1.0" encoding="ASCII"?>', '')
    amt_assignment_answer = amt_assignment_answer.replace(
        ' xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionFormAnswers.xsd"', ''
    )
    root = ET.fromstring(amt_assignment_answer)
    d = {}
    for child in root:
        d[child[0].text] = child[1].text
    # Assuming workerId and voucherCode present.
    amt_worker_id = d['workerId']
    amt_voucher_code = d['voucherCode']
    amt_voucher_hash = hashlib.sha512(bytes(amt_voucher_code, 'ascii')).hexdigest()
    return (amt_worker_id, amt_voucher_code, amt_voucher_hash)


def verify_voucher_hash(
        mydb, mycursor, amt_worker_id, amt_assignment_id, amt_voucher_hash):
    """Check if provided voucher hash matches database etnry."""
    entry_exist = False
    is_match = False
    str_match = 'MISMATCH'
    redeem_voucher = False
    db_voucher_id = None

    sql = "SELECT voucher_id, voucher_hash, status_code FROM voucher WHERE amt_worker_id=%s AND amt_assignment_id=%s"
    vals = (amt_worker_id, amt_assignment_id)
    mycursor.execute(sql, vals)

    myresult = mycursor.fetchall()
    n_row = len(myresult)
    if n_row == 0:
        print('      WARNING: No voucher entry for queried worker-assignment.')
        str_match = "UNKNOWN"
        str_status = "UNKNOWN"
    else:
        entry_exist = True
        if n_row > 1:
            print(
                'WARNING: More than one entry for queried worker-assignment. '
                'Using the first one and ignoring the other {0} '
                'entries.'.format(n_row - 1)
            )
        db_voucher_id = myresult[0][0]
        db_voucher_hash = myresult[0][1]
        db_status_code = myresult[0][2]
        if amt_voucher_hash == db_voucher_hash:
            is_match = True
            str_match = 'MATCH'
        if db_status_code == STATUS_VALID:
            str_status = 'valid'
        elif db_status_code == STATUS_REDEEMED:
            str_status = 'redeemed'
        else:
            str_status = 'expired'

    print(
        '      Assignment ID: {0} | voucher code {1} | {2}'.format(
            amt_assignment_id, str_match, str_status
        )
    )

    if entry_exist and is_match and (db_status_code == 0):
        redeem_voucher = True
    return redeem_voucher, db_voucher_id


def update_voucher_status(mydb, mycursor, db_voucher_id, status_code):
    """Update status code for voucher.

    Status Codes:
        0 - valid, not redeemed, not expired
        1 - not valid, redeemed
        2 - not valid, not redeemed, expired
    """
    sql = "UPDATE voucher SET status_code={0:d} WHERE voucher_id={1:d}".format(status_code, db_voucher_id)
    mycursor.execute(sql)
    mydb.commit()
    print('      SET status_code={0:d} | {1} row(s) affected'.format(status_code, mycursor.rowcount))


if __name__ == "__main__":
    # Parse arguments.
    parser = argparse.ArgumentParser()
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
            "Indicates that live HITs should be reviewed. If flag is not "
            "used, only Sandbox HITs are reviewed."
        )
    )
    parser.set_defaults(live=False)
    parser.add_argument(
        "-v", "--verbose", type=int, default=0,
        help="Increase output verbosity."
    )
    args = parser.parse_args()
    main(args.aws_profile, args.live, args.verbose)
