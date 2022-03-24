from urllib import response
from botocore.exceptions import ClientError
from cmath import nan
import logging
import json



#create the topic - communication channel
def createSNSTopic(name, sns_client):

    try:
     return sns_client.create_topic(Name=name)
    except ClientError as e:
     logging.error(e)

#create  subscription 
def createASubscription(topicArn, protocol, endpoint, sns_client): 

    try: 
       return sns_client.subscribe(TopicArn=topicArn, Protocol=protocol, Endpoint=endpoint)
    except ClientError as e: 
        logging.error(e) 

def addPermission(sns_client, sns_policy, TopicArn):
      try:
        sns_client.set_topic_attributes(
            TopicArn=TopicArn,
            AttributeName='Policy',
            AttributeValue=json.dumps(sns_policy)
        )
      except ClientError as e:
        logging.error(e)

def listOfSubscribers(sns_client, TopicArn): 
   try:
     return sns_client.list_subscriptions_by_topic(
         TopicArn= TopicArn
      )
   except ClientError as e: 
      logging.error(e)

def deleteTopic(sns_client, TopicArn): 
   try: 
      response =  sns_client.list_subscriptions_by_topic(TopicArn=TopicArn)['Subscriptions']
      for subsriber in response:
             
             sns_client.unsubscribe(SubscriptionArn=subsriber['SubscriptionArn'])
      sns_client.delete_topic(TopicArn=TopicArn)
   except ClientError as e: 
      logging.error(e)

