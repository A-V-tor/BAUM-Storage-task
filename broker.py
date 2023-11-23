import aiokafka
import asyncio
from datetime import datetime
from json import dumps, loads
from database import LineSymbolCounter
from collections import Counter


async def produser_logic(file_name):
    producer = aiokafka.AIOKafkaProducer(
        bootstrap_servers="kafka:9092",
        value_serializer=lambda x: dumps(x).encode("utf-8"),
    )
    await producer.start()
    try:
        with open(file_name, "r") as f:
            for line in f.readlines():
                stringdatetime = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
                await producer.send_and_wait(
                    "my_topic",
                    {"datetime": stringdatetime, "title": f"{f.name}", "text": line},
                )
                asyncio.sleep(3)
                await producer.flush()
    finally:
        await producer.stop()


async def consumer_logic(session):
    consumer = aiokafka.AIOKafkaConsumer(
        "my_topic",
        bootstrap_servers="kafka:9092",
        value_deserializer=lambda m: loads(m.decode("ascii")),
    )
    await consumer.start()

    data = await consumer.getmany(timeout_ms=10000)
    while data:
        for _, messages in data.items():
            for msg in messages:
                len_value = Counter(msg.value["text"]).get("Х", 0) + Counter(
                    msg.value["text"]
                ).get("х", 0)
                datetime_note = datetime.strptime(
                    msg.value["datetime"], "%d.%m.%Y %H:%M:%S"
                )
                new_record = LineSymbolCounter(
                    datetime=datetime_note,
                    title=f"{msg.value['title']}",
                    text=f"{msg.value['text']}",
                    value_count=len_value,
                )
                session.add(new_record)
                await session.commit()

        data = await consumer.getmany(timeout_ms=10000)

    await consumer.stop()


async def main_logic_kafka(file_name, session):
    await asyncio.gather(produser_logic(file_name), consumer_logic(session))
