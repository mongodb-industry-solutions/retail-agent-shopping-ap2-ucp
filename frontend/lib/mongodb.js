import { MongoClient } from "mongodb";
import { EJSON } from "bson";

// Validate required environment variables
if (!process.env.MONGODB_URI) {
  throw new Error('Invalid/Missing environment variable: "MONGODB_URI"');
}
if (!process.env.DATABASE_NAME) {
  throw new Error('Invalid/Missing environment variable: "DATABASE_NAME"');
}

const uri = process.env.MONGODB_URI;
const dbName = process.env.DATABASE_NAME;

//  Provide a custom appName to identify connections in MongoDB monitoring tools (e.g., Atlas, db.currentOp)
const options = {
  appName: "sse-store-events",
};

let client;
let clientPromise;
const changeStreams = new Map();

//  Reuse a single global MongoClient instance to avoid creating new connections on every hot reload
if (!global._mongoClientPromise) {
  client = new MongoClient(uri, options);
  clientPromise = client.connect();
  global._mongoClientPromise = clientPromise;
} else {
  clientPromise = global._mongoClientPromise;
}

/**
 * Open or reuse a MongoDB Change Stream for the given key.
 * This function stores ChangeStreams in memory (Map) to avoid duplicates.
 */
async function getChangeStream(filter, key) {
  if (!changeStreams.has(key)) {
    const client = await clientPromise;
    const db = client.db(dbName);

    // Convert filter to Extended JSON for compatibility with $match
    const filterEJSON = EJSON.parse(JSON.stringify(filter));

    const options = { fullDocument: "updateLookup" };
    const pipeline = [{ $match: filterEJSON }];

    const changeStream = db.watch(pipeline, options);

    changeStream.on("change", (change) => {
      console.log("Change: ", change);
    });

    changeStream.on("error", (error) => {
      console.log("Error: ", error);
    });

    changeStreams.set(key, changeStream);
  }
  return changeStreams.get(key);
}

export { clientPromise, dbName, getChangeStream };