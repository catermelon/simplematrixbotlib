# Examples Usage

The following examples will demonstrate simplematrixbotlib usage:

## Echo Bot

This code creates a handler called `echo` that listens `on_text`. The `echo` handler checks that a message starts with `!echo ` and was sent by a different user. If so, the `send_text` method is used to send the rest of the message to the same room. The code within the dunder boilerplate creates a `Creds` object using environment variables and runs the bot.

```python
from simplematrixbotlib import Creds, Bot, on_text, Message, Room, run


@on_text
async def echo(message: Message, room: Room, bot: Bot):
    if message.args[0] != "!echo" or message.sender_id == bot.user_id:
        return

    response = ' '.join(message.args[1:])

    await room.send_text(response, reply_to_event_id=message.event_id)


if __name__ == '__main__':
    creds = Creds.from_env(
        homeserver="MATRIX_HOMESERVER",
        user="MATRIX_USER",
        password="MATRIX_PASSWORD"
    )

    run(creds=creds, handlers=[echo])

```
