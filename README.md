## simplematrixbotlib 3.0.0

simplematrixbotlib is a Python bot library for the Matrix ecosystem built on [matrix-nio](https://github.com/poljar/matrix-nio).

- [Git Repository](https://codeberg.org/imbev/simplematrixbotlib) ([Mirror](https://github.com/i10b/simplematrixbotlib))
- [Package](https://pypi.org/project/simplematrixbotlib/)
- [Documentation](https://simplematrixbotlib.readthedocs.io)
- [Matrix Chat](https://matrix.to/#/#simplematrixbotlib:matrix.org)

## Features

- [x] Hands-off approach: get started with just 10 lines of code
- [x] End-to-end encryption support
- [x] Limited verification support (device only)
- [x] Easily extendable configuration
- [x] User access management
- [x] Access to the matrix-nio library for advanced features

## Setup

### simplematrixbotlib can be installed from PyPi or cloned from github.

Install from PyPi:

```
python -m pip install simplematrixbotlib
```

Using end-to-end encryption requires matrix-nio[e2e] `python -m pip install "matrix-nio[e2e]"`

Download from git repository:

```
git clone --branch master https://codeberg.org/imbev/simplematrixbotlib.git
```

## Example Usage

```python
# echo.py
# Example:
# randomuser - "!echo example"
# echo_bot - "example"

from simplematrixbotlib import Creds, Bot, on_text, Message, Room, run


@on_text
async def echo(message: Message, room: Room, bot: Bot):
    if message.args[0] != "!echo" or message.sender_id == bot.user_id:
        return

    response = ' '.join(message.args[1:])

    await room.send_text(response, reply_to_event_id=message.event_id)


if __name__ == '__main__':
    creds = Creds.from_env(homeserver="MATRIX_HOMESERVER", user="MATRIX_USER", password="MATRIX_PASSWORD")

    run(creds=creds, handlers=[echo])

```
