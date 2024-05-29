# src/aggregate.py
import asyncio
import datetime
import os
import logging

from motor.motor_asyncio import AsyncIOMotorClient


MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME')
COLLECTION_NAME = os.getenv('COLLECTION_NAME')

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]





async def aggregate_data(dt_from, dt_upto, group_type):

    logging.info(f"----------{dt_from,dt_upto,group_type}")
    group_format = {
        "hour": "%Y-%m-%dT%H:00:00",
        "day": "%Y-%m-%dT00:00:00",
        "month": "%Y-%m-01T00:00:00"
    }.get(group_type)

    if not group_format:
        raise ValueError("Invalid group_type. Use 'hour', 'day' or 'month'.")

    pipeline = [
        {"$match": {"dt": {"$gte": dt_from, "$lte": dt_upto}}},
        {"$group": {
            "_id": {"$dateToString": {"format": group_format, "date": "$dt"}},
            "total": {"$sum": "$value"}
        }},
        #{"$sort": {"_id": 1}}
    ]
    pipeline_all = [
        {"$match": {}}
    ]

    result = collection.aggregate(pipeline_all)#.to_list(length=100)
    logging.info(f"----------------{result}")
    dataset = [item['total'] for item in result]
    labels = [item['_id'] for item in result]

    return {"dataset": dataset, "labels": labels}
