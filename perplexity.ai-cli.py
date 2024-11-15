import json
from json import dumps, loads
from random import getrandbits
from threading import Thread
from time import sleep, time
from uuid import uuid4

from requests import Session
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from websocket import WebSocketApp

console = Console()


class Perplexity:
    def __init__(self):
        self.session = Session()
        self.user_agent = {
            "User-Agent": "Ask/2.4.1/224 (iOS; iPhone; Version 17.4) isiOSOnMac/false",
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
        )(), "Failed to initialize as an anonymous user."
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


def display_markdown(md_content: str):
    """Display formatted Markdown content in the terminal."""
    markdown = Markdown(md_content)
    console.print(Panel(markdown, expand=False, border_style="cyan"))


def display_references(references):
    """Display references in a structured manner."""
    if not references:
        console.print(Panel("No references found.", expand=False, border_style="red"))
        return
    console.print(f"[bold cyan]References:[/bold cyan]")
    for i, ref in enumerate(references, 1):
        console.print(
            f"[bold yellow]{i}.[/bold yellow] [blue]{ref['name']}[/blue] - [green]{ref['url']}[/green]"
        )


def main():
    console.print(
        "[bold purple]Welcome to the Perplexity AI CLI interface![/bold purple]"
    )
    console.print(
        "Type your question and press [bold]Enter[/bold]. Enter [bold cyan]$refs[/bold cyan] to view references."
    )
    # type `Crtl+c` to exit the program
    console.print("Type `Crtl+c` to exit the program!")

    console.print(
        Panel("Start by asking a question!", expand=False, border_style="magenta")
    )

    references = []

    while True:
        try:
            prompt = console.input("[bold green]> [/bold green]").strip()
            if not prompt:
                continue

            if prompt.lower() == "$refs":
                display_references(references)
                continue

            console.print("[gray]Loading...[/gray]")
            perplexity = Perplexity()
            response = list(perplexity.generate_answer(prompt))
            if not response:
                console.print(Panel("No response was generated.", border_style="red"))
                continue

            # Last complete response
            last_answer = response[-1]

            data = json.loads(last_answer["text"])
            # print(data)
            display_markdown(data["answer"])

        except KeyboardInterrupt:
            console.print("\n[bold red]Exiting as requested by the user![/bold red]")
            break


if __name__ == "__main__":
    main()
