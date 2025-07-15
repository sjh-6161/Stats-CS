from demoparser2 import DemoParser
from data import *

def parse(rounds: List[Round], match_id: UUID, parser: DemoParser):
    messages = parser.parse_event("chat_message")

    message_objects = []

    if isinstance(messages, list): return []

    for _, row in messages.iterrows():
        round_id = None
        for round in rounds:
            if row['tick'] > round.freeze_time_end_tick:
                round_id = round.id

        if round_id == None: continue

        message_objects.append(Message(
            player_id=row['user_steamid'],
            round_id=round_id,
            match_id=match_id,
            message=row['chat_message']
        ))

    return message_objects
