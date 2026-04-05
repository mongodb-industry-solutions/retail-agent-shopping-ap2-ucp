import { NextResponse } from "next/server";
import { ObjectId } from "mongodb";
import { clientPromise, dbName } from "@/lib/mongodb";

export async function POST(request) {
    const { 
        filter={}, 
        projection ={},
        options={}, 
        databaseName = dbName, 
        collectionName 
    } = await request.json();
    const client = await clientPromise;
    const db = client.db(databaseName);
    const collection = db.collection(collectionName);

    if(filter['_id']){
        filter['_id'] = new ObjectId(filter['_id'])
    }

    const result = await collection
        .find(filter, projection, options )
        .toArray()
    
    return NextResponse.json({ documents: result || null }, { status: 200 });
}