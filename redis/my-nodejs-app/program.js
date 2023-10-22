console.log("TEST1");

const createAndRunClient = async () => {
    try {
        console.log("TEST2")

        const redis = require('redis');
        let client = redis.createClient({
            legacyMode: true ,
            url: 'redis://redis:6379',
        });
        client.on('error', err => console.log('Redis Client Error', err));
        await client.connect();

        // console.log("client", client)
        console.log("TEST3")

        await client.set('key', 'value');
        const value = await client.get('key');

        console.log("value", value)
    } catch (error) {
        console.error('An error occurred:', error);
    }

    console.log("TEST4")
};

createAndRunClient();
