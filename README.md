# AMT Voucher Task

In many cases, we would like to allow Amazon Mechanical Turk (AMT) workers to complete a task on a website that we created and are hosting. At the same time, we would like to have maximum decoupling between our website and AMT requirements. The following code provides the pieces necessary to achieve this goal. 

In brief, this code uses AMT's External Question format and a voucher system. On completion of the task, workers are given a randomly generated voucher code. When the voucher code is generated, we store a hashed copy in a MySQL database. The worker submits the (unhashed) code via AMT. An example python script shows how you can automatically pay workers that submit a valid voucher code. A minimum working demo is included.

Throughout this document generality is achieved by using two stand in variables:
1. `<user>` refers to your user name on the host server.
2. `mywebsite.com` refers to your registered domain name.
The demo code must be modified in two places to work. First, the HIT configuration `demo.json` must be modified so that the QuestionUrl string points to a real URL. Second, the amt_index.php file must be modified so that the `amt-redirect-form` points to a real URL.

I'll also assume the text editor nano is available and use that throught the document. Similar command line text editors can be used instead.

## Requirements
The following code assumes:
* Access to a server using a LAMP stack.
* Ownership of a registered domain name and corresponding corresponding SSL certificate.
* Ownership of Amazon Web Service (AWS) credentials.
* A python environment with boto3.

The following code has been tested using the following stack:
* Ubuntu 18.04.2 LTS
* Apache/2.4.29 (Ubuntu)
* PHP 7.0.0
* MySQL Server version: 5.7.26-0ubuntu0.18.04.1 (Ubuntu)

The code will likely work with other configurations, but has not been tested. However, PHP 7.0.0 is required in order to use the more secure rand_int function.

The document is organized into three sections:
* 1. Setup.
* 2. Creating HITs.
* 3. Voucher verification.
* 4. Adding to a custom website.

## 1. Setup
* 1.1 Clone project to the host server.
* 1.2 Setup AWS credentials.
* 1.3 Setup MySQL credentials and database.
* 1.4 (optional) Place the demo webfiles in appropriate location.

### 1.1 Clone project to the host server.
Clone the project repository from GitHub by executing the command `git clone https://github.com/roads/amt-voucher.git`. The remainder of the document assumes the closed project resides at `/home/<user>/amt-voucher/`.

### 1.2 Setup AWS credentials.
AWS credentials are assumed to be stored at `/home/<user>/.aws/credentials` using profiles. See the Boto3 configuration [guide](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html) for how to create this file. For example, this file might contain the following information:
```
[default]
aws_access_key_id=foo1
aws_secret_access_key=bar1

[profile_1]
aws_access_key_id=foo2
aws_secret_access_key=bar2

[profile_2]
aws_access_key_id=foo3
aws_secret_access_key=bar3
```
The profile names will be used to create HITs.

### 1.3 Setup MySQL credentials and database.
To setup the MySQL database we will be creating a credentials file and creating the relevant `amt_voucher` database.

MySQL credentials are assumed to be stored in the file `/home/<user>/.mysql/credentials`. If you have not done so already, create the hidden directory `.mysql`. Then open the text file `credentials` by typing `nano .mysql/credentials`

Add the following block of text indicating the credentials to use when accessing the database `amt_voucher`.
```
[amt_voucher]
servername = localhost
username = <mysql_username>
password = <myql_password>
database = amt_voucher

```
where `<mysql_username>` and `<myql_password>` have been appropriate substituted with your MySQL login credentials. When your done exit and save as `credentials` when prompted.

This file is intentionally located outside the website root directory to prevent the general public from obtaining these credentials. Note that you can also add credentials for other databases to this file.

The actual MySQL database is created by logging into MySQL and executing ``mysql> SOURCE amt_voucher/sql/install_db_voucher.sql;``. Note that this code will only create a database called **amt_voucher** if it does not already exist.

When running our webcode, the server needs to know where to find the MySQL credentials. We'll achieve this by setting an environment variable. Environment variables can be set by editing your website's vhost file. The path to this file will look like `/etc/apache2/sites-available/mywebsite.com-le-ssl.conf`. Open this file with with root privledges using `sudo nano /etc/apache2/sites-available/mywebsite.com-le-ssl.conf` and add the line like shown below:
```
ServerAdmin admin@host
DocumentRoot /var/www/my_website
ServerName local.server
ServerAlias local.alias.server
SetEnv MYSQL_CRED /home/<user>/.mysql/credentials <-- add this line
```
When you're done, save your changes. Then call `sudo service apache2 restart` to make the changes go into effect.

The the sole table of the database `amt_voucher` is called `voucher`. If you look at the fields of `voucher`, there is a field called `status_code`. This field is used to denote the status of a particular code. The follow codes are used:
* 0 - created, not redeemed, not expired
* 1 - created, redeemed
* 2 - created, not redeemed, expired

### 1.4 Place the demo webfiles in appropriate location.
Inside the `amt-voucher` project, there is a directory called `website` which contains the necessary webfiles to create a demo webpage. This directory can be moved to the desired location inside the website root directory. For example, by executing the command `cp amt-voucher/demo/website/ /var/www/mywebsite.com/public_html/voucher-demo/`.

If everything is setup correctly, you should not be able to visit https://mywebsite.com/voucher-demo/. When you click the "Generate Voucher Code" button, you should see a random alphanumeric 12 character code. If the MySQL database is set up correctly, this code will be hashed and stored in the MySQL database.

Note that the PHP file `post-voucher.php` includes some simple checks to prevent a user abuse. Specifically only one voucher code can be requested for each unique pair of worker ID and assignment ID. As a consequence, if the demo website is visited without being redirected from AMT, the worker ID and assignment ID are both blank. Once a code has been generated for a blank worker ID and blank assignment ID combo, you cannot generate a new code. If you want to be able to generate a code, you must remove this "blank" entry from the `amt_voucher` database. Refreshing the page removes the voucher code.

## 2. Creating HITs.
To create a HIT you must first define a HIT configuration. The variable names directly correspond to variable names used by the Boto3 library. These are specified in JSON format. Examples can be found `amt-voucher/demo/hit_configs/`. Of particular importance are the fields `QuestionUrl`, `Reward`, and `MaxAssignments`. The QuestionUrl tell AMT which page to load for the preview and the actual HIT. In our case, this is a simple web page with basic instructions that also allows a worker to submit a voucher code. The `Reward` and `MaxAssignments` determine the amount workers are paid (in USD) and how many assignments to create for the HIT.

Once a HIT configuration has been created, you can create a HIT by calling the python script `create_hit.py`. This script requires to arguments: the path to the HIT configuration file and the name of an AWS profile. You can only use a profile name which is included in the shared credentials file (e.g., `.aws/credentials`). For example, you could call the script using the following command: ``python create_hit.py hit_config.json 'roads'``.

By default, HITs are deployed to the Sandbox site and do not use actaul money. If you would like to create a live HIT that uses real money, you must also use the `--live` flag. For example: ``python create_hit.py hit_config.json 'roads' --live``. If you are going to deploy a live HIT double check your configuration to make sure you are paying the correct amount. Once the HIT is created and accepted by a worker, it cannot be retracted.

To aid in keeping track of HITs, HIT IDs are saved to a text file in the directory `.amt-voucher/logs/` called `hit_live.txt` or `hit_sandbox.txt` depending on whether the HIT is live or not.

When creating HITs it should be noted that AWS charges a commission. If HITs involve fewer than ten assignments, the comission is 20%. IF HITs involve ten or more assingments the commission is 40%.

## 3. Voucher verification.
Following best practice, the literal voucher codes are not stored in the MySQL database. Instead the codes are stored as sha512 hashes. To check if a worker has submitted a valid code, there submission must be retrieved from AMT's servers, hashed, and compared to the hash value in our database. The example script `review_vouchers.py` demonstrates how one could review and approve submitted vouchers. This script is only a simple example and does not handle all edge cases.

## 4. Adding to a custom website.
The AMT voucher functionality can be achieved by placing the `amt-voucher` directory inside you website directory. Following the example shown in the demo `index.php` this functionality can then be integrated into your website.


## Additional Information
SEE: https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_ExternalQuestionArticle.html

### Defining Qualifications
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
    
    Not eligable if worker has qualification 32O4TCGYF79JBVY6IAIULRFG5O5D17
        {
            "QualificationTypeId":"32O4TCGYF79JBVY6IAIULRFG5O5D17",
            "Comparator":"DoesNotExist",
            "ActionsGuarded":"DiscoverPreviewAndAccept"
        }
