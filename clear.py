
from S3 import deleteBucket 
from SNS import deleteTopic
from Lambda.Lambda import deleteLambdaFunction


def deleteAllResource(bucketName, TopicArn, LambdaName, s3_resource, lambda_client,  sns_client): 

     if(bucketName != ""):
         deleteBucket(s3_resource, bucketName)
     if(TopicArn != ""): 
         deleteTopic(sns_client, TopicArn)
     if(LambdaName != ""): 
         deleteLambdaFunction(lambda_client, LambdaName)
     print("delete")
