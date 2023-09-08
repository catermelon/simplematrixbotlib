"""
Example Usage:

random_user
    !reply something

reply_bot
    reply:
        something
"""

import simplematrixbotlib as botlib

creds = botlib.Creds("https://home.server", "user", "pass")
bot = botlib.Bot(creds)
PREFIX = '!'

def check_command(room, message, cmd) -> tuple:
    match = botlib.MessageMatch(room, message, bot, PREFIX)
    if not match.is_not_from_this_bot(): return False, None
    if not match.prefix() or not match.command(cmd): return False, None
    return True, match

@bot.listener.on_message_event
async def echo(room, message):
    is_command, match = check_command(room, message, "reply")
    if not is_command: return

    await bot.api.send_text_message(
        room.room_id,
        " ".join(arg for arg in match.args()),
        reply_to=message.event_id
    )


bot.run()
