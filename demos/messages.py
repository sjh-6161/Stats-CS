from demoparser2 import DemoParser
from data import *
from pandas import DataFrame

def parse(rounds: List[Round], match_id: UUID, chat_message_df: DataFrame):
    # messages = parser.parse_event("chat_message")

    message_objects = []

    if isinstance(chat_message_df, list): return []

    for _, row in chat_message_df.iterrows():
        round_id = None
        for round in rounds:
            if row['tick'] > round.freeze_time_end_tick:
                round_id = round.id

        if round_id == None: continue

        message_objects.append(Message(
            player_id=row['user_steamid'],
            round_id=round_id,
            match_id=match_id,
            message=row['chat_message'],
            tick=row['tick']
        ))

    return message_objects
