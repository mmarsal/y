console.log("Running script.");

const { Redis } = require('ioredis');
let client = null;

const createAndRunClient = async () => {
    try
    {
        console.log("Creating client.");
        client = new Redis('redis://redis:6379');
        client.on('error', err => console.log('Redis Client Error', err));

        console.log("Initializing test data.");
        await initializeTestData();

        console.log("Running access patterns.");

        console.log("1. access pattern: Post tweet.")
        await postTweet();

        console.log("2. access pattern: Post reply.");
        await postReply();

        await editTweet();
        await readTimeline();

        console.log("5. access pattern: Delete tweet.")
        await deleteTweet("tweet:10", "user:1");

        console.log("6. access pattern: delete User.");
        await deleteUser();

    } catch (error) {
        console.error('An error occurred:', error);
    }
};

const initializeTestData = async () => {
    // Three users
    for (let i = 1; i < 4; i++) {
        const key = "user:" + i;
        const value = JSON.stringify({
            userId: i,
            name: "User" + i,
        });
        await client.set(key, value);
    }

    // Followers
    for (let i = 1; i < 4; i++) {
        const key = "user:" + i + ":followers";
        let value = [1, 2, 3];
        value = value.filter((val) => val !== i);
        await client.sadd(key, value);
        // const test = await client.smembers(key);
        // console.log(test)
    }
};

const postTweet = async () =>
{
    // Save tweet
    const tweetKey = "tweet:10";
    const tweetValue = JSON.stringify({
        id: 10,
        text: "Moin, moin.",
        likes: 0,
    });
    await client.set(tweetKey, tweetValue);

    // Save tweet in the user
    await client.sadd("user:1:tweets", 10);

    // Get followers
    const followers = await client.smembers("user:1:followers");

    // Add tweet to their timeline
    followers.map(async (follower) => {
        await client.sadd("timeline:" + follower, 10);
    })
};

const postReply = async () =>
{
    // Create reply
    const value = JSON.stringify({
        id: 1,
        text: "Hallo zurück.",
        likes: 0,
    });
    await client.set("reply:1", value);

    // Add reply id to tweet
    await client.sadd("tweet:10:replies", 1);

    // Add reply id to user
    await client.sadd("user:2:replies", 1);
};

const readTimeline = async () =>
{

};

const editTweet = async () =>
{

};

const deleteTweet = async (tweetId, userId) =>
{
    // delete tweet
    await client.del(tweetId);

    // get followers of user1
    const followers = await client.smembers(userId + ":followers");

    // delete tweet 10 on every follower timeline
    followers.map(async (follower) => {
        await client.srem("timeline:" + follower, tweetId);
    })
};

const deleteUser = async () =>
{
    // Add new tweet
    const tweetKey = "tweet:20";
    const tweetValue = JSON.stringify({
        id: 20,
        text: "Eigener Tweet",
        likes: 0,
    });
    await client.set(tweetKey, tweetValue);

    // Save tweet for user
    await client.sadd("user:1:tweets", 20);

    // Get followers
    const followers = await client.smembers("user:1:followers");

    // Add tweet to their timeline
    followers.map(async (follower) => {
        await client.sadd("timeline:" + follower, 20);
    })

    // remove all written tweets from user:1
    const tweets = await client.smembers("user:1:tweets");
    tweets.map(async (tweet) => {
        await deleteTweet("tweet:" + tweet, "user:1");
    })

    // delete user
    await client.del("user:1");
};

createAndRunClient();
