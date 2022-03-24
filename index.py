import boto3
import logging
import json
import urllib.parse
import urllib.error
import time
from botocore.exceptions import ClientError

rekognition=boto3.client('rekognition', region_name='us-east-1')
sns_client=boto3.client('sns', region_name='us-east-1')
dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')
dynamo_resource= boto3.resource('dynamodb', region_name='us-east-1')

def detectText(bucket,key):
    try:
          response=rekognition.detect_text(Image={'S3Object':{'Bucket':bucket,'Name':key}})
          print(response)
          return response
    except ClientError as e: 
         logging.error(e)
        
def createTable(tableName):
    try: 
     return dynamodb_client.create_table(
            TableName=tableName, 
            KeySchema=[
                {
                    'AttributeName': 'ImageName',
                    'KeyType': 'HASH'  # Partition key

                }
            ],
            AttributeDefinitions=[
               {
                    'AttributeName': 'ImageName',
                    'AttributeType': 'S'
               },
            ],

            ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
            }

        
        )
    except ClientError as e: 
        logging.error(e)

def putItem(tableName, itemInfo):
        try: 
          table = dynamo_resource.Table(tableName)
          time.sleep(10)
          return table.put_item(
                Item=itemInfo
           )
        except ClientError as e: 
                logging.error(e)

def containsTable(tableName): 
        try: 
          response = dynamodb_client.list_tables()

          return tableName in response['TableNames']
        except ClientError as e: 
                logging.error(e)

def handler(event, context): 
    
    message = json.loads(event['Records'][0]['Sns']['Message'])
    bucket = message['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(message['Records'][0]['s3']['object']['key'])
    print(message)
    print(bucket)
    print(key)
    try:
        
            #detect_text using rekognito
            response = detectText(bucket,key)
            
            textDetections = response['TextDetections']
            detectedText = {}
            for text in textDetections:
                DetectedText= str(text['DetectedText']);
                Confidence = str(text['Confidence'])
                detectedText[DetectedText] =  Confidence
             
            #check if the table is created
            containsTable2 = containsTable('cpdLambda1906581')
        
            #if the table is not created yet 
            if not containsTable2 : 
              createTable('cpdLambda1906581')
            
            #add the detected text as an item in dynamo db
            putItem('cpdLambda1906581', {'ImageName': key, 'DetectedText' : {'SS': detectedText } })


            #check if detected texts has hazard or danger
            for textObject in detectedText:
                if  textObject=="HAZARD" or textObject=="Danger":
                  
                  #register phone number 
                  response = sns_client.create_sms_sandbox_phone_number(
                  PhoneNumber='+250785971983',
                  LanguageCode='en-US'
                  )
                  #check if the result has danger or  hazard 
                  sns_client.publish(
                  PhoneNumber="+250785971983",
                  Message="A rekognito image {} have the Danger or Hazard word".format(key)
                  )

            
    except Exception as e:
            print(e)