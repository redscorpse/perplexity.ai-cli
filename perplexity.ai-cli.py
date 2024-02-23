#!/usr/bin/env python

"""
__source__  = "https://github.com/HelpingAI/Helpingai_T2/blob/main/Helpingai_T2/__init__.py"
__author__  = "OEvortex"
__version__ = "0.3"
"""
#pip install websocket-client requests

from uuid import uuid4
from time import sleep, time
from threading import Thread
from json import loads, dumps
from random import getrandbits
from websocket import WebSocketApp
from requests import Session


class Perplexity:
    def __init__(self):
        self.session = Session()
        self.user_agent = {
            "User-Agent": "Ask/2.4.1/224 (iOS; iPhone; Version 17.1) isiOSOnMac/false",
            "X-Client-Name": "Perplexity-iOS",
        }
        self.session.headers.update(self.user_agent)
        self.t = format(getrandbits(32), "08x")
        self.sid = loads(
            self.session.get(
                url=f"https://www.perplexity.ai/socket.io/?EIO=4&transport=polling&t={self.t}"
            ).text[1:]
        )["sid"]
        self.n = 1
        self.base = 420
        self.finished = True
        self.last_uuid = None
        assert (
            lambda: self.session.post(
                url=f"https://www.perplexity.ai/socket.io/?EIO=4&transport=polling&t={self.t}&sid={self.sid}",
                data='40{"jwt":"anonymous-ask-user"}',
            ).text
            == "OK"
        )(), "Failed to ask the anonymous user."
        self.ws = self._init_websocket()
        self.ws_thread = Thread(target=self.ws.run_forever).start()
        while not (self.ws.sock and self.ws.sock.connected):
            sleep(0.1)

    def _init_websocket(self):
        def on_open(ws):
            ws.send("2probe")
            ws.send("5")

        def on_message(ws, message):
            if message == "2":
                ws.send("3")
            elif not self.finished:
                if message.startswith("42"):
                    message = loads(message[2:])
                    content = message[1]
                    if "mode" in content:
                        content.update(loads(content["text"]))
                    content.pop("text")
                    if (not ("final" in content and content["final"])) or (
                        "status" in content and content["status"] == "completed"
                    ):
                        self.queue.append(content)
                    if message[0] == "query_answered":
                        self.last_uuid = content["uuid"]
                        self.finished = True
                elif message.startswith("43"):
                    message = loads(message[3:])[0]
                    if (
                        "uuid" in message and message["uuid"] != self.last_uuid
                    ) or "uuid" not in message:
                        self.queue.append(message)
                        self.finished = True

        cookies = ""
        for key, value in self.session.cookies.get_dict().items():
            cookies += f"{key}={value}; "
        return WebSocketApp(
            url=f"wss://www.perplexity.ai/socket.io/?EIO=4&transport=websocket&sid={self.sid}",
            header=self.user_agent,
            cookie=cookies[:-2],
            on_open=on_open,
            on_message=on_message,
            on_error=lambda ws, err: print(f"WebSocket error: {err}"),
        )

    def generate_answer(self, query):
        self.finished = False
        if self.n == 9:
            self.n = 0
            self.base *= 10
        else:
            self.n += 1
        self.queue = []
        self.ws.send(
            str(self.base + self.n)
            + dumps(
                [
                    "perplexity_ask",
                    query,
                    {
                        "frontend_session_id": str(uuid4()),
                        "language": "en-GB",
                        "timezone": "UTC",
                        "search_focus": "internet",
                        "frontend_uuid": str(uuid4()),
                        "mode": "concise",
                    },
                ]
            )
        )
        start_time = time()
        while (not self.finished) or len(self.queue) != 0:
            if time() - start_time > 30:
                self.finished = True
                return {"error": "Timed out."}
            if len(self.queue) != 0:
                yield self.queue.pop(0)
        self.ws.close()


# ------------------------------------------------------ #
# ------------------------------------------------------ #
# ------------------------------------------------------ #


class tColor:
    # "\033[38;2;181;76;210m" == rgb(181,76,210)
    reset = '\033[0m'
    bold = '\033[1m'
    red = '\033[91m'
    green = '\033[92m'
    yellow = '\033[93m'
    blue = '\033[94m'
    purple = '\033[38;2;181;76;210m'
    lavand = '\033[38;5;140m'
    aqua = '\033[38;5;109m'
    aqua2 = '\033[38;5;158m'


def main():
    # Start a continuous conversation with the user
    print("Welcome to perplexity.ai CLI!")
    print("Enter/Paste your content. Enter + Ctrl-D (or Ctrl-Z in windows) to send it.")
    print("To check the references from last response, type `$refs`.\n")
    while True:
        answer = "––– no answer –––"

        # Get a prompt from the user
        prompt = ""
        while True:
            print(f"{tColor.bold} >  {tColor.lavand}", end="")
            while True:
                try:
                    line = input()
                except EOFError:
                    break
                prompt += line + '\n'
            print(tColor.reset, end="")

            if ("$refs" in prompt):
                refs = ""
                for ref in references:
                    refs += f"- {ref['name']}\n  {ref['url']}\n"
                print(f"\nREFERENCES:\n{refs}")
                prompt = ""
                break

            # Generate a response using the Perplexity AI
            answer = list(Perplexity().generate_answer(prompt))
            last_answer = dict(answer[-2]) #because last one is empty
            answer = last_answer['answer']
            references = last_answer['web_results']
            print(tColor.aqua2, end='\n', flush=True)
            for char in answer:
                print(char, end='', flush=True)
                sleep(0.02)
            print(tColor.reset, end='\n\n', flush=True)

if __name__ == "__main__":
    try:
        while True:
            main()
    except KeyboardInterrupt:
        exit(f"\n\n{tColor.red}Aborting!{tColor.reset}")

