from ws4py.client.threadedclient import WebSocketClient
import json
from collections import deque
import threading
import time

leds = ['misc', 'linkedevents', 'kerrokantasi', 'respa', 'servicemap']
led_qs = {name : deque() for name in leds}

class ApiRequestMonitor(WebSocketClient):
    # def __init__(self, **kwargs):
    #     WebSocketClient.__init__(self, **kwargs)
    #     # self.last_rcvd_ts = time.perf_counter()
    #     # self.led_qs = {name : deque() for name in leds}

    def opened(self):
        print("Opened connection")

    def closed(self, code, reason=None):
        print("Closed down", code, reason)

    def received_message(self, m):
        # debugging the interval between bursts of messages
        # ...seems to be either ~5s, ~7.5s, ~12.5s (quite rarely), ~15s (rarely) or even ~20s (rarely)
        # if time.perf_counter() - self.last_rcvd_ts > 0.1:
        #     print('------------------------------')
        #     print(time.perf_counter() - self.last_rcvd_ts)
        #     print('------------------------------')
        #     self.last_rcvd_ts = time.perf_counter()
        data = json.loads(m.data.decode('utf-8'))
        if 'api_name' in data:
            led_qs[data['api_name']].append(data)
            # print(data['api_name'])
        else:
            led_qs['misc'].append(data)
            # print(data['request'])

#generator yielding lengths of queues
def deque_len():
    while True:
        yield [len(l) for l in led_qs.values()]
#function (run in own thread) to consume above generator
def print_deque_len():
    length = deque_len()
    for l in length:
        print(l)
        time.sleep(5)

#generator yielding (FIFO) request objects
def req_from_q(q):
    while True:
        try:
            yield q.popleft()
        except IndexError:
            yield None
#function (run in own thread) to consume above generator
#   sleeps for 0.2 if there's nothing in the queue OR
#   blinks for a second and remains off for 0.2 if we did get an item
def blink(q, duration=1):
    requests = req_from_q(q)
    for req in requests:
        if not req:
            time.sleep(0.2)
            continue
        apiname = req['api_name'] if 'api_name' in req else 'misc'
        print('BLINK ON {} {}'.format(req['response'], apiname))
        time.sleep(duration)
        print('BLINK OFF {}'.format(apiname))
        time.sleep(0.2)

if __name__ == '__main__':
    #debug print the lengths of the queues to make sure they don't grow forever
    threading.Thread(target=print_deque_len).start()

    #individual threads (& deques) for individual LEDs / APIs
    for q in led_qs.values():
        threading.Thread(target=blink, args=(q,)).start()

    try:
        ws = ApiRequestMonitor(url='ws://logstash.hel.ninja:3249', protocols=['http-only', 'chat'])
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()
