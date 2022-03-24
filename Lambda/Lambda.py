import logging
import os
from botocore.exceptions import ClientError
import zipfile

def createZipFile ():
   with zipfile.ZipFile('function.zip', 'w') as zipObj:
   #Add file to obj
     zipObj.write('index.py')

   with open('function.zip', 'rb') as file_data:
        bytes_content = file_data.read()
        return bytes_content

def createLambdaFunction(functionName, role, lambda_client ):
   
    try:
        return lambda_client.create_function(
            FunctionName=functionName,
            Runtime='python3.6',
            Role=role,
            Handler='index.handler',
            Code={
                'ZipFile': createZipFile(),
            },
            Timeout= 63
        )
     
    except ClientError as e: 
        logging.error(e)

def deleteLambdaFunction(lambda_client, functionName): 
    try: 
        return lambda_client.delete_function(
        FunctionName=functionName,
        )
    except ClientError as e: 
        logging.error(e)

def addPermissionLambda(lambda_client, functionName, principal, statementId):
    try: 
        return lambda_client.add_permission(
        FunctionName=functionName,
        Action= "lambda:InvokeFunction",
        StatementId=statementId,
        Principal=principal,
        )
    except ClientError as e: 
        logging.error(e)
