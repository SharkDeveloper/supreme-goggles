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
    dt_from = datetime.datetime.fromisoformat(dt_from)
    dt_upto = datetime.datetime.fromisoformat(dt_upto)


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
        {"$sort": {"_id": 1}}
    ]
    pipeline_all = [
        {"$match": {}}
    ]

    result = await collection.aggregate(pipeline).to_list(length=None)
    logging.info(f"----------------{result}")


    current = dt_from
    all_dates = []
    while current <= dt_upto:
        all_dates.append(current.strftime(group_format))
        if group_type == 'hour':
            current += datetime.timedelta(hours=1)
        elif group_type == 'day':
            current += datetime.timedelta(days=1)
        elif group_type == 'month':
            next_month = current.month % 12 + 1
            year = current.year + (current.month + 1 > 12)
            current = current.replace(year=year, month=next_month, day=1)


    data_dict = {date: 0 for date in all_dates}

    for item in result:
        data_dict[item['_id']] = item['total']

    dataset = list(data_dict.values())
    labels = list(data_dict.keys())

    return {"dataset": [dataset], "labels": [labels]}
