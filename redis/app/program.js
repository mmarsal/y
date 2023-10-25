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

        console.log("Running access patterns.");
        await postTweet();
        await deleteTweet();
        await postReply();
        await readTimeline();
        await editTweet();
        await deleteUser();
    } catch (error) {
        console.error('An error occurred:', error);
    }
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
