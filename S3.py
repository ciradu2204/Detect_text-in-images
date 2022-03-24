
from cmath import nan
import logging
from multiprocessing.connection import Client
from botocore.exceptions import ClientError
import json
import os


#a function to create a bucket
def create_bucket(bucket_name,s3_client): 

    try:
        return s3_client.create_bucket(Bucket=bucket_name, ObjectOwnership='BucketOwnerEnforced')
    except ClientError as e: 
        logging.error(e)

def addBucket_Notification_configuration(s3_client, bucketName, newConfiguration): 
    try: 
        s3_client.put_bucket_notification_configuration(
            Bucket=bucketName,
            NotificationConfiguration= {'TopicConfigurations' :[newConfiguration]}
        )
    except ClientError as e: 
        logging.error(e)
def listBucket(s3_client, bucketName): 
    try: 
        return s3_client.list_objects(
            Bucket=bucketName
        )
    except ClientError as e: 
        logging.error(e)

def deleteBucket(s3_resource, bucketName):
    try:
        bucket= s3_resource.Bucket(bucketName)
        bucket.objects.all().delete()
        bucket.delete()
    except ClientError as e: 
        logging.error(e)

def uploadToBucket(s3_client, bucketName, fileName): 

    try:
        result = s3_client.upload_file(
            fileName,
            bucketName,
            os.path.basename(fileName)
        )
        print("successfully uploaded")
    except ClientError as e: 
        logging.error(e)

def addPermissionBucket(bucketName, policy, s3_client):
    stringPolicy = json.dumps(policy)
    try: 

     return s3_client.put_bucket_policy(
         Bucket = bucketName, 
         Policy= stringPolicy
     )
    except ClientError as e: 
        logging.error(e)