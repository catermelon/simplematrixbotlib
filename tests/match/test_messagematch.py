from simplematrixbotlib.match import MessageMatch, Match
from unittest import mock

mock_room = mock.MagicMock()

mock_event = mock.MagicMock()
mock_event.body = "p!help example"

mock_event2 = mock.MagicMock()
mock_event2.body = "p!help"

mock_bot = mock.MagicMock()

prefix = "p!"
prefix2 = "!!"

match = MessageMatch(mock_room, mock_event, mock_bot, prefix)
match2 = MessageMatch(mock_room, mock_event, mock_bot)
match3 = MessageMatch(mock_room, mock_event, mock_bot, prefix2)
match4 = MessageMatch(mock_room, mock_event2, mock_bot, prefix)


def test_init():
    assert issubclass(MessageMatch, Match)
    assert match._prefix == prefix


def test_command():
    assert match.command("Help") == False


def test_contains():
    assert match.contains("!h") == False
    assert match.contains("lp exam") == False
    assert match.contains("nothing") == False


match = MessageMatch(mock_room, mock_event, mock_bot, prefix)


def test_init():
    assert issubclass(MessageMatch, Match)
    assert match._prefix == prefix
