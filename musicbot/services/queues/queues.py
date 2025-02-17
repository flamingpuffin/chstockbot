from asyncio import Queue as _Queue
from asyncio import QueueEmpty as Empty
import asyncio
from typing import Dict


class Queue(_Queue):
    _queue: list = []

    def clear(self):
        self._queue.clear()


queues: Dict[int, Queue] = {}


async def put(chat_id: int, **kwargs) -> int:
    if chat_id not in queues:
        queues[chat_id] = Queue()
    await queues[chat_id].put({**kwargs})
    return queues[chat_id].qsize()


def get(chat_id: int) -> Dict[str, str]:
    if chat_id in queues:
        try:
            return queues[chat_id].get_nowait()
        except Empty:
            return {}
    return {}

def getlist(chat_id: int):
    if chat_id in queues:
        return queues[chat_id]._queue

def is_empty(chat_id: int) -> bool:
    if chat_id in queues:
        return queues[chat_id].empty()
    return True

def qsize(chat_id: int) -> int:
    if chat_id in queues:
        return queues[chat_id].qsize()
    return 0

def task_done(chat_id: int):
    if chat_id in queues:
        try:
            queues[chat_id].task_done()
        except ValueError:
            pass


def clear(chat_id: int):
    if chat_id in queues:
        if queues[chat_id].empty():
            raise Empty
        else:
            queues[chat_id].clear()
    raise Empty


async def main():
    for i in range(10):
        n = await put(1,a=i)
        print(qsize(1),n,queues)
    for i in getlist(1):
        print(qsize(1),i,getlist(1))

if __name__ == '__main__':
    asyncio.run(main())