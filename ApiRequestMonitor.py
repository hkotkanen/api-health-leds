from ws4py.client.threadedclient import WebSocketClient
from pprint import pprint
import json
import queue
from collections import deque
import threading
import time

leds = ['misc', 'linkedevents', 'kerrokantasi', 'respa', 'servicemap']
led_qs = {name : deque() for name in leds}

# class Api2LedBroker():
#
#     def __init__(self):
#         #init led strip
#         #init queue
#         # self.q = queue.Queue()
#         self.led_qs = {name : queue.Queue() for name in leds}
#
#     def add_msg(self, msgdict):
#         # print(msgdict['response'])
#         msg = msgdict['response'] if 'response' in msgdict else "----WTF----"
#         if 'api_name' in msgdict:
#             # print(msgdict['api_name'])
#             msg += ' ' + msgdict['api_name']
#             self.led_qs[msgdict['api_name']].append(msgdict)
#         else:
#             msg += ' ' + msgdict['request']
#             self.led_qs['misc'].append(msgdict)
#         # self.q.put(msgdict)
#         print(msg)
#
#     def blink(q, delay=0.1):
#
#         pass

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

        # print([len(l) for l in led_qs.values()])

        # if 'uptimerobot' in data['agent'].lower():
        #     print('{} returned to UptimeRobot/{}'.format(data['response'], data['clientip']))
        # elif '127.0.0.1' in data['clientip']:
        #     print('{} returned from {}, requested from localhost'.format(data['response'], data['request']))
        # else:
        #     try:
        #         print('{} returned from {}, requested from {}'.format(data['response'], data['api_name'], data['clientip']))
        #     except KeyError as e:
        #         print('KeyError:'+str(e), data)
        #     except e:
        #         print(e, m)

def deque_len():
    while True:
        yield [len(l) for l in led_qs.values()]

def print_deque_len():
    length = deque_len()
    for l in length:
        print(l)
        time.sleep(5)

def req_from_q(q):
    while True:
        try:
            yield q.popleft()
        except IndexError:
            yield None

def blink(q, delay=1):
    # while True:
    #     try:
    #         req = q.popleft()
    #         apiname = req['api_name'] if 'api_name' in req else 'misc'
    #         print('BLINK ON {} {}'.format(req['response'], apiname))
    #         time.sleep(delay)
    #         print('BLINK OFF {}'.format(apiname))
    #     except IndexError as e:
    #         pass
    #     except Exception as e:
    #         print(e)
    requests = req_from_q(q)
    for req in requests:

        if not req:
            time.sleep(0.2)
            continue

        apiname = req['api_name'] if 'api_name' in req else 'misc'
        print('BLINK ON {} {}'.format(req['response'], apiname))
        time.sleep(delay)
        print('BLINK OFF {}'.format(apiname))
        time.sleep(0.2)



if __name__ == '__main__':
    #debug print the lengths of the queues
    # printer = threading.Thread(target=print_deque_len)
    # printer.start()
    threading.Thread(target=print_deque_len).start()
    for q in led_qs.values():
        threading.Thread(target=blink, args=(q,), daemon=True).start()
    try:
        ws = ApiRequestMonitor(url='ws://logstash.hel.ninja:3249', protocols=['http-only', 'chat'])
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()
