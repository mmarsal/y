import boto3
from datetime import date
import time
import uuid
from credentials import *
import unittest

client = None

def set_db():
    global client
    client = boto3.client('dynamodb', 
      endpoint_url='http://dynamo:8000', 
      region_name='eu-central-1',
      aws_access_key_id=aws_access_key_id,
      aws_secret_access_key=aws_secret_access_key
    )
    client.list_tables()

def create_app_table():
    return client.create_table(
        TableName="twitter",
        KeySchema=[
            {"AttributeName": "PK", "KeyType": "HASH"},
            {"AttributeName": "SK", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "SK", "AttributeType": "S"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 10, "WriteCapacityUnits": 10},
    )

def delete_app_table():
    try:
        return client.delete_table(TableName="twitter")
    except:
        return False

def parse_id_from_key(key):
    return key.split("#")[-1]

def save_user(user):
    return client.put_item(
        TableName="twitter",
        Item=user
    )

# AP6
def find_user(primaryKey, sortKey):
    item = client.get_item(
        TableName="twitter",
        Key={
          'PK': { 'S': primaryKey },
          'SK': { 'S': sortKey }
        }
    )
    return item['Item'] if 'Item' in item else False

def add_to_followers(primaryKey, follower):
    response = client.put_item(
            TableName="twitter",
            Item={
                'PK': {'S': primaryKey},
                'SK': {'S': f"FOLLOWER#{parse_id_from_key(follower['PK']['S'])}"},
                'Name': {'S': follower['Name']['S']},
            },
        )
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        return client.get_item(
            TableName='twitter',
            Key={
                'PK': {'S': primaryKey},
                'SK': {'S': f"FOLLOWER#{parse_id_from_key(follower['PK']['S'])}"},
            }
        )

def post_tweet(primaryKey, tweet):
    client.put_item(
        TableName='twitter',
        Item={
            'PK': {'S': primaryKey},
            'SK': {'S': f"TWEET#{tweet['id']['S']}"},
            'id': {'S': tweet['id']['S']},
            'text': {'S': tweet['text']['S']},
            'likes': {'N': tweet['likes']['N']},
            'CreatedAt': { 'N': tweet['CreatedAt']['N']}
        },
    )
    item = client.query(
        TableName="twitter",
        KeyConditionExpression='PK = :pk AND begins_with(SK, :follower)',
        ExpressionAttributeValues={
            ':pk': { 'S': primaryKey },
            ':follower': { 'S': 'FOLLOWER#' }
        },
    )
    followers = item['Items']
    for follower in followers:
        response2 = client.put_item(
            TableName='twitter',
            Item={
                'PK': {'S': f"USER#{parse_id_from_key(follower['SK']['S'])}"},
                'SK': {'S': f"TIMELINE#{tweet['id']['S']}"},
                'tweetId': {'S': tweet['id']['S']},
                'text': {'S': tweet['text']['S']},
                'likes': {'N': tweet['likes']['N']},
                'CreatedAt': { 'N': tweet['CreatedAt']['N']}
            },
        )
    if response2['ResponseMetadata']['HTTPStatusCode'] == 200:
        return client.query(
            TableName="twitter",
            KeyConditionExpression='PK = :pk AND begins_with(SK, :timeline)',
            ExpressionAttributeValues={
                ':pk': { 'S': f"USER#{parse_id_from_key(follower['SK']['S'])}" },
                ':timeline': { 'S': 'TIMELINE#' }
            },
        )

def post_reply(author, user, tweet, reply):
    client.put_item(
        TableName='twitter',
        Item={
            'PK': {'S': f"USER#{parse_id_from_key(author['PK']['S'])}"},
            'SK': {'S': f"TWEET#{tweet['id']['S']}#{reply['id']['S']}"},
            'id': {'S': reply['id']['S']},
            'text': {'S': reply['text']['S']},
            'likes': {'N': reply['likes']['N']},
            'CreatedAt': { 'N': reply['CreatedAt']['N']}
        },
    )
    item = client.query(
        TableName="twitter",
        KeyConditionExpression='PK = :pk AND begins_with(SK, :follower)',
        ExpressionAttributeValues={
            ':pk': { 'S': f"USER#{parse_id_from_key(author['PK']['S'])}" },
            ':follower': { 'S': 'FOLLOWER#' }
        },
    )
    followers = item['Items']
    for follower in followers:
        response2 = client.put_item(
            TableName='twitter',
            Item={
                'PK': {'S': f"USER#{parse_id_from_key(follower['SK']['S'])}"},
                'SK': {'S': f"TIMELINE#{tweet['id']['S']}#{reply['id']['S']}"},
                'id': {'S': reply['id']['S']},
                'text': {'S': reply['text']['S']},
                'likes': {'N': reply['likes']['N']},
                'CreatedAt': { 'N': reply['CreatedAt']['N']}
            },
        )
    if response2['ResponseMetadata']['HTTPStatusCode'] == 200:
        return client.query(
            TableName="twitter",
            KeyConditionExpression='PK = :pk AND begins_with(SK, :timeline)',
            ExpressionAttributeValues={
                ':pk': { 'S': f"USER#{parse_id_from_key(author['PK']['S'])}" },
                ':timeline': { 'S': 'TIMELINE#' }
            },
        )

def edit_tweet(primaryKey, tweetId, new_text):

    response = client.update_item(
        TableName="twitter",
        Key={
            'PK': {'S': primaryKey},
            'SK': {'S': f"TWEET#{tweetId}"}
        },
        UpdateExpression='SET #text = :new_text',
        ExpressionAttributeNames={
            '#text': 'text'
        },
        ExpressionAttributeValues={
            ':new_text': {'S': new_text}
        }
    )


    followers_query = client.query(
        TableName="twitter",
        KeyConditionExpression='PK = :pk AND begins_with(SK, :follower)',
        ExpressionAttributeValues={
            ':pk': {'S': primaryKey},
            ':follower': {'S': 'FOLLOWER#'}
        },
    )

    followers = followers_query.get('Items', [])
    for follower in followers:
        client.update_item(
            TableName="twitter",
            Key={
                'PK': {'S': f"USER#{parse_id_from_key(follower['SK']['S'])}"},
                'SK': {'S': f"TIMELINE#{tweetId}"}
            },
            UpdateExpression='SET #text = :new_text',
            ExpressionAttributeNames={
                '#text': 'text'
            },
            ExpressionAttributeValues={
                ':new_text': {'S': new_text}
            }
        )

    return response

def get_user_tweets(primaryKey):
    response = client.query(
        TableName="twitter",
        KeyConditionExpression='PK = :pk AND begins_with(SK, :tweet)',
        ExpressionAttributeValues={
            ':pk': {'S': primaryKey},
            ':tweet': {'S': 'TWEET#'}
        }
    )

    tweets = response.get('Items', [])
    return tweets

def read_timeline(primaryKey):
    timeline_query = client.query(
        TableName="twitter",
        KeyConditionExpression='PK = :pk AND begins_with(SK, :timeline)',
        ExpressionAttributeValues={
            ':pk': {'S': primaryKey},
            ':timeline': {'S': 'TIMELINE#'}
        },
    )
    return timeline_query.get('Items', [])

def delete_tweet(primaryKey, tweet_id):
    # Löschen des Tweets aus der Tweet-Entität
    client.delete_item(
        TableName='twitter',
        Key={'PK': {'S': primaryKey}, 'SK': {'S': f"TWEET#{tweet_id}"}}
    )

    # Löschen des Tweets aus den Timelines aller Follower
    followers = client.query(
        TableName="twitter",
        KeyConditionExpression='PK = :pk AND begins_with(SK, :msg)',
        ExpressionAttributeValues={
            ':pk': {'S': primaryKey},
            ':msg': {'S': 'FOLLOWER#'}
        },
    )['Items']

    for follower in followers:
        client.delete_item(
            TableName='twitter',
            Key={'PK': {'S': follower['SK']['S']}, 'SK': {'S': f"TIMELINE#{tweet_id}"}}
        )

def delete_user(user_id):
    user_tweets_response = client.query(
        TableName='twitter',
        KeyConditionExpression='#pk = :pk',
        ExpressionAttributeNames={'#pk': 'PK'},
        ExpressionAttributeValues={':pk': {'S': f'USER#{user_id}'}}
    )

    user_tweets = user_tweets_response.get('Items', [])

    for tweet in user_tweets:
        tweet_id = tweet.get('id', {}).get('S')  # Zugriff auf das tatsächlich vorhandene Feld 'id'

        if tweet_id:
            client.delete_item(
                TableName='twitter',
                Key={'PK': {'S': tweet['PK']['S']}, 'SK': {'S': tweet['SK']['S']}}
            )

            followers_response = client.query(
                TableName='twitter',
                KeyConditionExpression='#pk = :pk',
                ExpressionAttributeNames={'#pk': 'PK'},
                ExpressionAttributeValues={':pk': {'S': tweet['PK']['S']}}
            )

            for follower in followers_response.get('Items', []):
                client.delete_item(
                    TableName='twitter',
                    Key={'PK': {'S': follower['SK']['S']}, 'SK': {'S': f'TIMELINE#{tweet_id}'}}
                )

    client.delete_item(
        TableName='twitter',
        Key={'PK': {'S': f'USER#{user_id}'}, 'SK': {'S': f'USER#{user_id}'}}
    )
