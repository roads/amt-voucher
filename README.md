# AMT Voucher Task

Tools to add Amazon Mechanical Turk (AMT) functionality to an existing task using the AMT's External Question format and a voucher code system. On completion of the task, workers are given a unique voucher code which they submit via AMT. A separate MySQL database keeps track of voucher codes and a python script automatically pays workers that submit a valid voucher code. Voucher codes are stored as sha512 hashes.

## Requirements
* Tested with a LAMP server configuration.
* PHP 7.0.0 (use of rand_int)
* MySQL credentials stored at .mysql/credentials. The appropriate database details should be included under the `[aws_voucher]` section.
* AWS credentials sorted at .aws/credentials

## Deployment
place amt pieces
    hit_config.json
    

## TODO
post-voucher.php: How to handle path to credentials?
drop-in functionality
    Only creates voucher codes when task website re-directed from AMT.
Script to create a voucher code if worker encounters issues and does not recieve a code.
Script to expire a voucher code.
Script(s) to update voucher status_code
change all references to database name `amt_voucher` to variable that loads from this config file
    using section `amt_voucher`

## Notes

## Assumed directory structure
Local
```
amt-voucher
+-- /projects
+-- /records
+-- /sql
+-- /collect.php
```

Host
```
/path/to/public_html/amt-voucher
+-- </my_project_0>
+-- </my_project_1>
```

## Components
### Included in website directory
* ``index_amt.php`` - AMT webpage handling the HIT preview, external website link, and voucher submission. [TODO This is intended to be a drop-in file.]
* ``css/bootstrap-grid.css``
* ``img/university.jpg``
* ``js/jquery-1.11.3.js``
* ``templates/organization_header.php``
* ``templates/preview.php`` - The AMT preview content.

### Other components
* ``create_hit.py`` - Python script to create an AMT HIT. Requires the path to an AMT configuration file and assumes users have created an AWS credentials file.
* ``amt_config.json`` - AMT configuration file.
* ``.aws/credentials`` - An AWS credentials file. 
* ``db_install.mysql`` - Script to install MySQL database for handling voucher codes.

## Database
Create the MySQL database on the host server. After logging into MySQL, execute:
``mysql> SOURCE db_install.sql;``

status_code
	0 - created, not redeemed, not expired
	1 - created, redeemed
	2 - created, not redeemed, expired



.. code-block:: none

    [default]
    servername = localhost
    username = <your_user_name>
    password = <your_password>


Assumptions
-----------
.mysql/credentials
redirect page is `index.html`

SEE: https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_ExternalQuestionArticle.html

Defining Qualifications
-----------------------
see https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_QualificationRequirementDataStructureArticle.html#ApiReference_QualificationType-IDs

General syntax
quals = [
    {
        "QualificationTypeId": "string",
        "Comparator": "LessThan"|"LessThanOrEqualTo"|"GreaterThan"|"GreaterThanOrEqualTo"|"EqualTo"|"NotEqualTo"|"Exists"|"DoesNotExist"|"In"|"NotIn",
        "IntegerValues": [
            123,
        ],
        "LocaleValues": [
            {
                "Country": "string",
                "Subdivision": "string"
            },
        ],
        "RequiredToPreview": True|False,
        "ActionsGuarded": "Accept"|"PreviewAndAccept"|"DiscoverPreviewAndAccept"
    },
]

Common qualifications
    Worker_Locale: 00000000000000000071
    see: https://www.iso.org/iso-3166-country-codes.html
    US only
        {
            "QualificationTypeId":"00000000000000000071",
            "Comparator":"EqualTo",
            "LocaleValues":[{
                "Country":"US"
          }]
        }

    Worker_​NumberHITsApproved: 00000000000000000040
    At least 100 HITs approved
        {
            "QualificationTypeId": "00000000000000000040",
            "Comparator": "GreaterThanOrEqualTo",
            "IntegerValues": [100]
        }

    Worker_​PercentAssignmentsApproved: 000000000000000000L0
    At least 90 percent of assignments approved.
        {
            "QualificationTypeId": "000000000000000000L0",
            "Comparator": "GreaterThanOrEqualTo",
            "IntegerValues": [90]
        }
    
    Not eligable if has qualification 32O4TCGYF79JBVY6IAIULRFG5O5D17
        {
            "QualificationTypeId":"32O4TCGYF79JBVY6IAIULRFG5O5D17",
            "Comparator":"Exist",
            "ActionsGuarded":"PreviewAndAccept"
        }
