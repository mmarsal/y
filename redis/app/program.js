console.log("Running script.");

const createAndRunClient = async () => {
    try {
        console.log("Creating client.");
        const redis = require('redis');
        let client = redis.createClient({
            url: 'redis://redis:6379',
        });
        client.on('error', err => console.log('Redis Client Error', err));
        await client.connect();

        console.log("Running access patterns.");
        await client.set('key', 'value');
        const value = await client.get('key');
        console.log("value", value)
    } catch (error) {
        console.error('An error occurred:', error);
    }
};

createAndRunClient();
