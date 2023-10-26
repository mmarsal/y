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
    console.log("2. access pattern: Post reply.");
    // Create reply
    const value = JSON.stringify({
        id: 1,
        text: "Hallo zurück.",
        likes: 0,
    });
    await client.set("reply:1", value);

    // Add reply id to tweet
    await client.sadd("tweet:1:replies", 1);

    // Add reply id to user
    await client.sadd("user:2:replies", 1);
};

const editTweet = async () => {
    console.log("3. access pattern: Edit tweet.");
    // Get tweet
    const tweetToEdit = client.get("tweet:1");

    // Edit tweet
    tweetToEdit.text = "Moin, moin. Wie geht es euch?";

    // Save edited tweet on same key
    client.set("tweet:1", JSON.stringify(tweetToEdit));
};

const readTimeline = async () => {

};

const deleteTweet = async () => {

};

const deleteUser = async () => {

};

createAndRunClient();
