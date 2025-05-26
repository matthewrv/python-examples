import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import sys
import time
import random
import threading
from collections import deque


ids = [
    "abcd",
    "efgh",
    "ijkl",
    "mnop",
    "qrst",
    "uvw",
    "xyz",
]


@dataclass
class LockedQueue:
    lock: threading.Lock = field(default_factory=threading.Lock)
    queue: deque = field(default_factory=deque)


class RateCounter:
    """Counts requests per sliding period of time."""

    def __init__(self):
        self._counter_lock = threading.Lock()
        self._counter: dict[str, LockedQueue] = {}

        rate_period = 1
        self._delta = timedelta(seconds=-rate_period)

        self._total_counter_lock = threading.Lock()
        self._total_counter = 0

    def _get_queue(self, id_: str) -> LockedQueue:
        # prevent race condition on inserting two different queues with same key
        with self._counter_lock:
            queue = self._counter.setdefault(id_, LockedQueue())
            return queue

    def add_request(self, id_: str, timestamp: datetime):
        locked_queue = self._get_queue(id_)
        queue, lock = locked_queue.queue, locked_queue.lock
        with lock:  # <-- try commenting this line and you will get race condition on queue iteration
            insert_pos = 0
            for i, value in enumerate(reversed(queue)):
                if timestamp >= value:
                    insert_pos = len(queue) - i
                    break

            queue.insert(insert_pos, timestamp)

            with self._total_counter_lock:
                self._total_counter += 1

    def get_count(self, id_: str) -> int:
        locked_queue = self._get_queue(id_)
        queue, lock = locked_queue.queue, locked_queue.lock

        with lock:
            timestamps_since = datetime.now() + self._delta
            while queue and queue[0] < timestamps_since:
                queue.popleft()
            count = len(queue)

        return count

    def clear_queues(self):
        with self._counter_lock:
            keys_snapshot = list(self._counter)

        for key in keys_snapshot:
            locked_queue = self._get_queue(key)
            queue, lock = locked_queue.queue, locked_queue.lock
            with lock:  # <-- try commenting this line and you will get race condition on queue iteration
                timestamps_since = datetime.now() + self._delta
                while queue and queue[0] < timestamps_since:
                    queue.popleft()

    def get_total_count(self):
        return self._total_counter


async def main():
    counter = RateCounter()

    errors = deque()
    stop_measures = threading.Event()
    measure_interval = 0.100  # 100ms
    clean_interval = 0.050  #  50ms

    producers = [
        threading.Thread(target=gen_requests, args=(counter, errors)),
        threading.Thread(target=gen_requests, args=(counter, errors)),
        threading.Thread(target=gen_requests, args=(counter, errors)),
        threading.Thread(target=gen_requests, args=(counter, errors)),
    ]

    consumer = threading.Thread(
        target=get_counts, args=(counter, measure_interval, stop_measures)
    )
    cleaner = threading.Thread(
        target=clean_queues, args=(counter, clean_interval, stop_measures)
    )

    threads = [
        *producers,
        consumer,
        cleaner,
    ]

    for thread in threads:
        thread.start()

    for thread in producers:
        thread.join()

    stop_measures.set()
    consumer.join()
    cleaner.join()

    print("-" * 20)

    while errors:
        print("Error:", errors.pop())

    print("Total number of requests is", counter.get_total_count())


def gen_requests(rate_counter: RateCounter, errors: deque):
    try:
        for _ in range(1000000):
            # use jitter to perform not only thread-safe appends, but also inserts on queue
            id_ = random.choice(ids)
            rate_counter.add_request(id_, datetime.now() + _jitter())
    except Exception as exc:
        errors.append(str(exc))
        raise


def _jitter():
    delta = random.random() * 10 - 5
    return timedelta(microseconds=delta)


def get_counts(
    rate_counter: RateCounter, measure_interval: float, stop_event: threading.Event
):
    while not stop_event.is_set():
        time.sleep(measure_interval)
        id_ = random.choice(ids)
        count = rate_counter.get_count(ids[0])
        sys.stdout.write(f"Current number of requests for id {id_}: {count}\n")


def clean_queues(
    rate_counter: RateCounter, clean_inteval: float, stop_event: threading.Event
):
    while not stop_event.is_set():
        time.sleep(clean_inteval)
        rate_counter.clear_queues()
        sys.stdout.write("Periodic cleaning completed\n")


if __name__ == "__main__":
    asyncio.run(main())
