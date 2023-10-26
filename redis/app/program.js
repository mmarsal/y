console.log("Running script.");

const { Redis } = require('ioredis');
let client = null;

const createAndRunClient = async () => {
    try {
        console.log("Creating client.");
        client = new Redis('redis://redis:6379');
        client.on('error', err => console.log('Redis Client Error', err));

        console.log("Initializing test data.");
        await initializeTestData();

        console.log("Running access patterns.");
        await postTweet();
        await postReply();
        await editTweet();
        await readTimeline();
        await deleteTweet();
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

const postTweet = async () => {
    console.log("1. access pattern: Post tweet.")
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

const postReply = async () => {

};

const readTimeline = async () => {

};

const editTweet = async () => {

};

const deleteTweet = async () => {

    console.log("5. access pattern: Delete tweet.")
    await client.del('tweet:10', function (err, response)
    {
        console.log(response);
    });

    // check if tweet 10 deleted successfully (value = null)
    const value = await client.get('tweet:10');
    if (value == null)
    {
        console.log('Tweet 10 deleted successfully')
    }

    // get followers of user1
    const followers = await client.smembers("user:1:followers");

    // delete tweet 10 on every follower timeline
    followers.map(async (follower) => {
        await client.srem("timeline:" + follower, 10);
    })
};

const deleteUser = async () => {

};

createAndRunClient();
