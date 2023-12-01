import pymongo
from bson.objectid import ObjectId
import json
import unittest

db = None


def set_db():
    mongo = pymongo.MongoClient("mongodb://root:hhn@mongo/admin")
    print(mongo.server_info()['version'])
    global db
    db = mongo.examples
    db.users.delete_many({})


def find_user(id):
    doc = db.users.find_one({'_id': ObjectId(id)})
    return doc or False


def find_users():
    return [user for user in db.users.find()]


def save_user(user):
    db.users.insert_one(user)
    return user


def add_to_followers(user_id, follower_id):
    db.users.update_one(
        {'_id': ObjectId(user_id)},
        {'$push': {'followers': {'_id': ObjectId(follower_id)}}}
    )
    return db.users.find_one({'_id': user_id})


def post_tweet(user, tweet):
    db.users.update_one(
        {'_id': ObjectId(user['_id'])},
        {'$push': {'tweets': tweet}}
    )
    db.users.update_many(
        {'_id': {'$in': [follower['_id'] for follower in user['followers']]}},
        {'$push': {'timeline': tweet}}
    )
    return [user for user in db.users.find()]


def read_timeline(user):
    return db.users.find_one(
        {'_id': ObjectId(user['_id'])},
        {'_id': 0, 'timeline': 1}
    )


def post_reply(tweet, reply):
    db.users.update_one(
        {'tweets._id': ObjectId(tweet['_id'])},
        {'$push': {'tweets.$.replies': reply}}
    )
    db.users.update_many(
        {'timeline._id': ObjectId(tweet['_id'])},
        {'$push': {'timeline.$.replies': reply}}
    )
    return [user for user in db.users.find()]


def edit_tweet(tweet):
    new_text = 'Moin, moin. Wie geht es euch?'
    db.users.update_one(
        {'tweets._id': ObjectId(tweet['_id'])},
        {'$set': {'tweets.$.text': new_text}}
    )
    db.users.update_many(
        {'timeline._id': ObjectId(tweet['_id'])},
        {'$set': {'timeline.$.text': new_text}}
    )
    return [user for user in db.users.find()]


def delete_tweet(user, tweet):
    db.users.update_one(
        {'_id': ObjectId(user['_id'])},
        {'$pull': {'tweets': {'_id': ObjectId(tweet['_id'])}}}
    )

    db.users.update_many(
        {'_id': {'$in': [follower['_id'] for follower in user['followers']]}},
        {'$pull': {'timeline': {'_id': ObjectId(tweet['_id'])}}}
    )

    return [user for user in db.users.find()]


def delete_user(user):
    for tweet in user['tweets']:
        db.users.update_many(
            {'_id': {'$in': [follower['_id'] for follower in user['followers']]}},
            {'$pull': {'timeline': {'_id': ObjectId(tweet['_id'])}}}
        )

    db.users.delete_one(
        {'_id': ObjectId(user['_id'])},
    )

    return [user for user in db.users.find()]
