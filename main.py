from cmath import nan
import boto3.session 
import time
import glob

from S3 import create_bucket
from S3 import addBucket_Notification_configuration
from S3 import uploadToBucket
from S3 import addPermissionBucket
from SNS import createSNSTopic
from SNS import createASubscription
from SNS import addPermission
from clear import deleteAllResource
from Lambda.Lambda import createLambdaFunction
from Lambda.Lambda import addPermissionLambda

aws_access_key_id='add-your-key'
aws_secret_access_key='add_your-key'
aws_session_token='add_your-key'

#create a session 
session=boto3.session.Session(aws_access_key_id, aws_secret_access_key, aws_session_token, 'us-east-1')
lab_role_urn="arn:aws:iam::253294972291:role/LabRole"
mybucketName = 'cpdbucket1906581'
lambdaFunctionName="cpdlambdfunction1906581"
topicArn=''

#create an s3 session 
s3_client = session.client('s3')
s3_resource = session.resource('s3')
#create an sns session 
sns_client = session.client('sns')
sns_resource = session.resource('sns')

#create a lambda  session
lambda_client = session.client('lambda')

#delete all resources
deleteAllResource(mybucketName, "arn:aws:sns:us-east-1:253294972291:cpdTopic1906581", lambdaFunctionName, s3_resource, lambda_client, sns_client)

#create an sns topic
mySnsTopicName='cpdTopic1906581'
topic = createSNSTopic(mySnsTopicName, sns_client)
topicArn=topic["TopicArn"]

#create the s3 bucket, assuming the region of us-east1
myBucket = create_bucket(mybucketName,s3_client)

#bucket policy to only allow rekognition to get 
bucketPolicy={
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Statement1",
            "Effect": "Allow",
            "Principal": {
                "Service": "rekognition.amazonaws.com"
            },
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::cpdbucket1906581/*"
        }
    ]
}

#add bucket to s3 
addPermissionBucket(mybucketName, bucketPolicy,  s3_client)

#create a lambda funtion
mylambdaFunction = createLambdaFunction(lambdaFunctionName, lab_role_urn, lambda_client)
lambdaFunctionName = mylambdaFunction["FunctionName"]

 #create a lambda subscription
subscribe = createASubscription(topicArn, "lambda", mylambdaFunction["FunctionArn"] , sns_client)

#add permission to the lambda function to execute
addPermissionLambda(lambda_client, lambdaFunctionName, "sns.amazonaws.com", "sns" )

sns_topic_policy = {
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": "sns:Publish",
            "Resource": topicArn,
            "Condition": {
                "ArnLike": {"AWS:SourceArn": f"arn:aws:s3:*:*:{mybucketName}"},
            }
        }
    ],
}
#create a permission to allow s3 to access sns 
addPermission(sns_client, sns_topic_policy, topicArn)

#create a new s3 event configuration for the topic
new_configuration = { 
        'TopicArn': topic["TopicArn"],
        'Events': [
            's3:ObjectCreated:Put',
        ]
    }
#configure s3 event notification to public to a topic when there is a put or post
addBucket_Notification_configuration(s3_client, mybucketName, new_configuration)
 

#upload to bucket 
allImages = glob.glob("./images/*")
for filename in allImages:
  uploadToBucket(s3_client, mybucketName, filename)
  time.sleep(10)
