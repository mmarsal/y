console.log("Running script.");

let client = null;

const createAndRunClient = async () => {
    try {
        console.log("Creating client.");
        const redis = require('redis');
        client = redis.createClient({
            url: 'redis://redis:6379',
        });
        client.on('error', err => console.log('Redis Client Error', err));
        await client.connect();

        console.log("Initializing test data.")
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
    // TODO: Followers
    /*for (let i = 1; i < 4; i++) {
        const key = "user:" + i + ":followers";
        let value = [1, 2, 3];
        value = value.filter((number) => number !== i);
        await client.sadd(key, value);
    }*/
};

const postTweet = async () => {
    await client.set('key', 'value');
    const value = await client.get('key');
    console.log("value", value)
};

const deleteTweet = async () => {

};

const postReply = async () => {

};

const readTimeline = async () => {

};

const editTweet = async () => {

};

const deleteUser = async () => {

};

createAndRunClient();
