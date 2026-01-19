import os
import re
from typing import Any, Generator, List, Optional, Tuple
from uuid import UUID
import psycopg2
from psycopg2 import sql, extras
from sequential_uuids.generators import uuid_time_nextval as uuid
from dotenv import load_dotenv
import traceback

load_dotenv()
regex = re.compile(r"([a-z])([A-Z])")

class DbClass:
    id: UUID

    def __init__(self, id: Optional[UUID] = None) -> None:
        self.id = id if id is not None else uuid()

    def __iter__(self) -> Generator[Any, Any, Any]:
        for attr, value in self.__dict__.items():
            yield attr, value

    def __name(self) -> str:
        return regex.sub(r"\1_\2", self.__class__.__name__).lower()

    def __fields(self) -> List[str]:
        return list(vars(self).keys())
    
    def __str__(self) -> str:
        string = ""

        for attr, value in self.__dict__.items():
            string += f"{attr}: {value}\n"

        return string

    def values(self) -> Tuple:
        return tuple(vars(self).values())

    def to_insert(self) -> Tuple[sql.SQL, Tuple]:
        query = sql.SQL("INSERT INTO {table} ({rows}) VALUES %s").format(
            table=sql.Identifier(self.__name()),
            rows=sql.SQL(", ").join(map(sql.Identifier, self.__fields())),
        )

        return (query, self.values())

    def to_create() -> str:
        raise NotImplementedError()
    
class Team(DbClass):
    name: str

    def __init__(
        self, 
        name: str, 
        id: Optional[UUID] = None
    ) -> None:
        super().__init__(id)
        self.name = name

    def to_create() -> str:
        return """
            CREATE TABLE IF NOT EXISTS team (
                id uuid PRIMARY KEY,
                name varchar(255) NOT NULL
            );
            """
    
class TournamentTeam(DbClass):
    player_id: str
    team_id: UUID
    tournament_name: str

    def __init__(
        self,
        player_id: str,
        team_id: UUID,
        tournament_name: str,
        id: Optional[UUID] = None
    ) -> None:
        super().__init__(id)
        self.player_id = player_id
        self.team_id = team_id
        self.tournament_name = tournament_name

    def to_create() -> str:
        return """
            CREATE TABLE IF NOT EXISTS tournament_team (
                id uuid PRIMARY KEY,
                player_id VARCHAR(500) REFERENCES player(steam_id),
                team_id uuid REFERENCES team(id),
                tournament_name varchar(500) NOT NULL
            );
        """

class Player(DbClass):
    steam_id: str
    name: str
    team_id: UUID

    def __init__(self, steam_id: str, name: str, team_id: UUID) -> None:
        self.steam_id = steam_id
        self.name = name
        self.team_id = team_id

    def to_create() -> str:
        return """
            CREATE TABLE IF NOT EXISTS player (
                steam_id VARCHAR(500) PRIMARY KEY,
                name varchar(255) NOT NULL,
                team_id uuid REFERENCES team(id)
            );
            """
    
    def __name(self) -> str:
        return regex.sub(r"\1_\2", self.__class__.__name__).lower()

    def __fields(self) -> List[str]:
        return list(vars(self).keys())
    
    def to_insert(self) -> Tuple[sql.SQL, Tuple]:
        query = sql.SQL("INSERT INTO {table} ({rows}) VALUES %s ON CONFLICT (steam_id) DO UPDATE SET name=EXCLUDED.name, team_id=EXCLUDED.team_id").format(
            table=sql.Identifier(self.__name()),
            rows=sql.SQL(", ").join(map(sql.Identifier, self.__fields())),
        )

        return (query, self.values())
    
class Match(DbClass):
    team_one_id: UUID
    team_two_id: UUID
    map: str
    file: str
    tournament: str

    def __init__(
        self,
        team_one_id: UUID,
        team_two_id: UUID,
        map: str,
        file: str,
        tournament: str,
        id: Optional[UUID] = None,
    ) -> None:
        self.team_one_id = team_one_id
        self.team_two_id = team_two_id
        self.map = map
        self.file = file
        self.tournament = tournament
        super().__init__(id)

    def to_create() -> str:
        return """
            CREATE TABLE IF NOT EXISTS match (
                id uuid PRIMARY KEY,
                team_one_id uuid NOT NULL REFERENCES team(id),
                team_two_id uuid NOT NULL REFERENCES team(id),
                map varchar(100) NOT NULL,
                file varchar(500) NOT NULL,
                tournament varchar(500) NOT NULL
            );
            """

class Round(DbClass):
    match_id: UUID
    freeze_time_end_tick: int
    end_official_tick: int
    round_end_reason: str
    t_rounds: int
    ct_rounds: int
    t_team_id: UUID
    ct_team_id: UUID
    winning_side: str
    winning_team_id: UUID
    losing_side: str
    losing_team_id: UUID

    def __init__(
        self,
        match_id: UUID,
        freeze_time_end_tick: int,
        end_official_tick: int,
        round_end_reason: str,
        t_rounds: int,
        ct_rounds: int,
        t_team_id: UUID,
        ct_team_id: UUID,
        winning_side: str,
        winning_team_id: UUID,
        losing_side: str,
        losing_team_id: UUID,
        id: Optional[UUID] = None,
    ) -> None:
        self.match_id = match_id
        self.freeze_time_end_tick = freeze_time_end_tick
        self.end_official_tick = end_official_tick
        self.round_end_reason = round_end_reason
        self.t_rounds = t_rounds
        self.ct_rounds = ct_rounds
        self.t_team_id = t_team_id
        self.ct_team_id = ct_team_id
        self.winning_side = winning_side
        self.winning_team_id = winning_team_id
        self.losing_side = losing_side
        self.losing_team_id = losing_team_id
        super().__init__(id)

    def to_create() -> str:
        return """
            CREATE TABLE IF NOT EXISTS round (
                id uuid PRIMARY KEY,
                match_id uuid NOT NULL REFERENCES match(id) ON DELETE CASCADE,
                freeze_time_end_tick int NOT NULL,
                end_official_tick int NOT NULL,
                round_end_reason varchar(255) NOT NULL,
                t_rounds int NOT NULL,
                ct_rounds int NOT NULL,
                t_team_id uuid NOT NULL REFERENCES team(id),
                ct_team_id uuid NOT NULL REFERENCES team(id),
                winning_side varchar(16) NOT NULL,
                winning_team_id uuid NOT NULL REFERENCES team(id),
                losing_side varchar(16) NOT NULL,
                losing_team_id uuid NOT NULL REFERENCES team(id)
            );
            """

class Plant(DbClass):
    match_id: UUID
    round_id: UUID
    tick: int
    site: str
    x: float
    y: float
    z: float

    def __init__(
        self,
        match_id: UUID,
        round_id: UUID,
        tick: int,
        site: str,
        x: float,
        y: float,
        z: float,
        id: Optional[UUID] = None,
    ) -> None:
        self.match_id = match_id
        self.round_id = round_id
        self.tick = tick
        self.site = site
        self.x = x
        self.y = y
        self.z = z
        super().__init__(id)

    def to_create() -> str:
        return """
            CREATE TABLE IF NOT EXISTS plant (
                id uuid PRIMARY KEY,
                match_id uuid NOT NULL REFERENCES match(id) ON DELETE CASCADE,
                round_id uuid NOT NULL REFERENCES round(id) ON DELETE CASCADE,
                tick int NOT NULL,
                site VARCHAR(2) NOT NULL,
                x float NOT NULL,
                y float NOT NULL,
                z float NOT NULL
            );
            """

class Kill(DbClass):
    match_id: UUID
    round_id: UUID
    assister_id: str
    attacker_id: str
    victim_id: str
    attacker_team_id: UUID
    assister_team_id: UUID
    victim_team_id: UUID
    attacker_x: float
    attacker_y: float
    attacker_z: float
    attacker_zone: str
    victim_x: float
    victim_y: float
    victim_z: float
    victim_zone: str
    assistedflash: bool
    attackerblind: bool
    attackerinair: bool
    headshot: bool
    noscope: bool
    penetrated: bool
    thrusmoke: bool
    distance: float
    dmg_armor: int
    dmg_health: int
    hitgroup: str
    weapon: str
    victim_weapon: str
    attacker_team: str
    assister_team: str
    victim_team: str
    t_alive: int
    ct_alive: int
    trade: bool
    traded: bool
    tick: int

    def __init__(
        self,
        match_id: UUID,
        round_id: UUID,
        assister_id: str,
        attacker_id: str,
        victim_id: str,
        attacker_team_id: UUID,
        assister_team_id: UUID,
        victim_team_id: UUID,
        attacker_x: float,
        attacker_y: float,
        attacker_z: float,
        attacker_zone: str,
        victim_x: float,
        victim_y: float,
        victim_z: float,
        victim_zone: str,
        assistedflash: bool,
        attackerblind: bool,
        attackerinair: bool,
        headshot: bool,
        noscope: bool,
        penetrated: int,
        thrusmoke: bool,
        distance: float,
        dmg_armor: int,
        dmg_health: int,
        hitgroup: str,
        weapon: str,
        victim_weapon: str,
        attacker_team: str,
        assister_team: str,
        victim_team: str,
        t_alive: int,
        ct_alive: int,
        trade: bool,
        traded: bool,
        tick: int,
        id: Optional[UUID] = None,
    ) -> None:
        self.match_id = match_id
        self.round_id = round_id
        self.assister_id = assister_id
        self.attacker_id = attacker_id
        self.victim_id = victim_id
        self.attacker_team_id = attacker_team_id
        self.assister_team_id = assister_team_id
        self.victim_team_id = victim_team_id
        self.attacker_x = attacker_x
        self.attacker_y = attacker_y
        self.attacker_z = attacker_z
        self.attacker_zone = attacker_zone
        self.victim_x = victim_x
        self.victim_y = victim_y
        self.victim_z = victim_z
        self.victim_zone = victim_zone
        self.assistedflash = assistedflash
        self.attackerblind = attackerblind
        self.attackerinair = attackerinair
        self.headshot = headshot
        self.noscope = noscope
        self.penetrated = penetrated
        self.thrusmoke = thrusmoke
        self.distance = distance
        self.dmg_armor = dmg_armor
        self.dmg_health = dmg_health
        self.hitgroup = hitgroup
        self.weapon = weapon
        self.victim_weapon = victim_weapon
        self.attacker_team = attacker_team
        self.assister_team = assister_team
        self.victim_team = victim_team
        self.t_alive = t_alive
        self.ct_alive = ct_alive
        self.trade = trade
        self.traded = traded
        self.tick = tick
        super().__init__(id)

    def to_create() -> str:
        return """
            CREATE TABLE IF NOT EXISTS kill (
                id uuid PRIMARY KEY,
                match_id uuid NOT NULL REFERENCES match(id) ON DELETE CASCADE,
                round_id uuid NOT NULL REFERENCES round(id) ON DELETE CASCADE,
                assister_id VARCHAR(32) REFERENCES player(steam_id),
                attacker_id VARCHAR(32) REFERENCES player(steam_id),
                victim_id VARCHAR(32) REFERENCES player(steam_id),
                attacker_team_id uuid REFERENCES team(id),
                assister_team_id uuid REFERENCES team(id),
                victim_team_id uuid NOT NULL REFERENCES team(id),
                attacker_x float,
                attacker_y float,
                attacker_z float,
                attacker_zone VARCHAR(32),
                victim_x float NOT NULL,
                victim_y float NOT NULL,
                victim_z float NOT NULL,
                victim_zone VARCHAR(32),
                assistedflash bool NOT NULL,
                attackerblind bool NOT NULL,
                attackerinair bool NOT NULL,
                headshot bool NOT NULL,
                noscope bool NOT NULL,
                penetrated int NOT NULL,
                thrusmoke bool NOT NULL,
                distance float,
                dmg_armor int NOT NULL,
                dmg_health int NOT NULL,
                hitgroup varchar(255) NOT NULL,
                weapon varchar(255) NOT NULL,
                victim_weapon varchar(255),
                attacker_team varchar(255),
                assister_team varchar(255),
                victim_team varchar(255),
                t_alive int NOT NULL,
                ct_alive int NOT NULL,
                trade bool NOT NULL,
                traded bool NOT NULL,
                tick int NOT NULL
            );
        """

class Damage(DbClass):
    match_id: UUID
    round_id: UUID
    attacker_id: str
    victim_id: str
    attacker_x: float
    attacker_y: float
    attacker_z: float
    attacker_zone: str
    victim_x: float
    victim_y: float
    victim_z: float
    victim_zone: str
    armor: int
    health: int
    dmg_armor: int
    dmg_health: int
    hitgroup: str
    tick: int
    weapon: str
    attacker_team: str
    victim_team: str

    def __init__(
        self,
        match_id: UUID,
        round_id: UUID,
        attacker_id: str,
        victim_id: str,
        attacker_x: float,
        attacker_y: float,
        attacker_z: float,
        attacker_zone: str,
        victim_x: float,
        victim_y: float,
        victim_z: float,
        victim_zone: str,
        armor: int,
        health: int,
        dmg_armor: int,
        dmg_health: int,
        hitgroup: str,
        tick: int,
        weapon: str,
        attacker_team: str,
        victim_team: str,
        id: Optional[UUID] = None,
    ) -> None:
        self.match_id = match_id
        self.round_id = round_id
        self.attacker_id = attacker_id
        self.victim_id = victim_id
        self.attacker_x = attacker_x
        self.attacker_y = attacker_y
        self.attacker_z = attacker_z
        self.attacker_zone = attacker_zone
        self.victim_x = victim_x
        self.victim_y = victim_y
        self.victim_z = victim_z
        self.victim_zone = victim_zone
        self.armor = armor
        self.health = health
        self.dmg_armor = dmg_armor
        self.dmg_health = dmg_health
        self.hitgroup = hitgroup
        self.tick = tick
        self.weapon = weapon
        self.attacker_team = attacker_team
        self.victim_team = victim_team
        super().__init__(id)

    def to_create() -> str:
        return """
            CREATE TABLE IF NOT EXISTS damage (
                id uuid PRIMARY KEY,
                match_id uuid NOT NULL REFERENCES match(id) ON DELETE CASCADE,
                round_id uuid NOT NULL REFERENCES round(id) ON DELETE CASCADE,
                attacker_id VARCHAR(32) REFERENCES player(steam_id),
                victim_id VARCHAR(32) NOT NULL REFERENCES player(steam_id),
                attacker_x float,
                attacker_y float,
                attacker_z float,
                attacker_zone VARCHAR(32),
                victim_x float NOT NULL,
                victim_y float NOT NULL,
                victim_z float NOT NULL,
                victim_zone VARCHAR(32),
                armor int NOT NULL,
                health int NOT NULL,
                dmg_armor int NOT NULL,
                dmg_health int NOT NULL,
                hitgroup VARCHAR(32) NOT NULL,
                tick int NOT NULL,
                weapon VARCHAR(255) NOT NULL,
                attacker_team varchar(255),
                victim_team varchar(255)
            );
        """
    
class PlayerDefault(DbClass):
    match_id: UUID
    round_id: UUID
    player_id: str
    team_id: UUID
    side: str
    x: float
    y: float
    z: float
    zone: str

    def __init__(
        self,
        match_id: UUID,
        round_id: UUID,
        player_id: str,
        team_id: UUID,
        side: str,
        x: float,
        y: float,
        z: float,
        zone: str,
        id: Optional[UUID] = None,
    ) -> None:
        self.match_id = match_id
        self.round_id = round_id
        self.player_id = player_id
        self.team_id = team_id
        self.side = side
        self.x = x
        self.y = y
        self.z = z
        self.zone = zone
        super().__init__(id)

    def to_create() -> str:
        return """
            CREATE TABLE IF NOT EXISTS player_default (
                id uuid PRIMARY KEY,
                match_id uuid NOT NULL REFERENCES match(id) ON DELETE CASCADE,
                round_id uuid NOT NULL REFERENCES round(id) ON DELETE CASCADE,
                player_id VARCHAR(32) NOT NULL REFERENCES player(steam_id),
                team_id uuid NOT NULL REFERENCES team(id),
                side VARCHAR(32) NOT NULL,
                x float NOT NULL,
                y float NOT NULL,
                z float NOT NULL,
                zone VARCHAR(32)
            );
        """
    
class WeaponFire(DbClass):
    match_id: UUID
    round_id: UUID
    attacker_id: str
    attacker_x: float
    attacker_y: float
    attacker_z: float
    attacker_zone: str
    attacker_pitch: float
    attacker_yaw: float
    attacker_team: str
    tick: int
    weapon: str
    silenced: bool

    def __init__(
        self,
        match_id: UUID,
        round_id: UUID,
        attacker_id: str,
        attacker_x: float,
        attacker_y: float,
        attacker_z: float,
        attacker_zone: str,
        attacker_pitch: float,
        attacker_yaw: float,
        attacker_team: str,
        tick: int,
        weapon: str,
        silenced: bool,
        id: Optional[UUID] = None,
    ) -> None:
        self.match_id = match_id
        self.round_id = round_id
        self.attacker_id = attacker_id
        self.attacker_x = attacker_x
        self.attacker_y = attacker_y
        self.attacker_z = attacker_z
        self.attacker_zone = attacker_zone
        self.attacker_pitch = attacker_pitch
        self.attacker_yaw = attacker_yaw
        self.attacker_team = attacker_team
        self.tick = tick
        self.weapon = weapon
        self.silenced = silenced
        super().__init__(id)

    def to_create() -> str:
        return """
            CREATE TABLE IF NOT EXISTS weapon_fire (
                id uuid PRIMARY KEY,
                match_id uuid NOT NULL REFERENCES match(id) ON DELETE CASCADE,
                round_id uuid NOT NULL REFERENCES round(id) ON DELETE CASCADE,
                attacker_id VARCHAR(32) REFERENCES player(steam_id),
                attacker_x float NOT NULL,
                attacker_y float NOT NULL,
                attacker_z float NOT NULL,
                attacker_zone VARCHAR(32),
                attacker_pitch float NOT NULL,
                attacker_yaw float NOT NULL,
                attacker_team VARCHAR(255) NOT NULL,
                tick int NOT NULL,
                weapon VARCHAR(255) NOT NULL,
                silenced boolean NOT NULL
            );
        """

class Buy(DbClass):
    player_id: str
    round_id: UUID
    match_id: UUID
    team_id: UUID
    side: str
    equipment_value: int
    balance: int

    def __init__(
        self,
        player_id: str,
        round_id: UUID,
        match_id: UUID,
        team_id: UUID,
        side: str,
        equipment_value: int,
        balance: int,
        id: Optional[UUID] = None,
    ) -> None:
        self.player_id=player_id
        self.round_id=round_id
        self.match_id=match_id
        self.team_id=team_id
        self.side=side
        self.equipment_value=equipment_value
        self.balance=balance
        super().__init__(id)
        
    def to_create() -> str:
        return """
            CREATE TABLE IF NOT EXISTS buy (
                id uuid PRIMARY KEY,
                player_id VARCHAR(500) NOT NULL REFERENCES player(steam_id),
                round_id uuid NOT NULL REFERENCES round(id) ON DELETE CASCADE,
                match_id uuid NOT NULL REFERENCES match(id) ON DELETE CASCADE,
                team_id uuid NOT NULL REFERENCES team(id),
                side VARCHAR(32) NOT NULL,
                equipment_value int NOT NULL,
                balance int NOT NULL
            );
        """
    
class Message(DbClass):
    player_id: str
    round_id: UUID
    match_id: UUID
    message: str
    tick: int

    def __init__(
        self,
        player_id: str,
        round_id: UUID,
        match_id: UUID,
        message: str,
        tick: int,
        id: Optional[UUID] = None,
    ) -> None:
        self.player_id=player_id
        self.round_id=round_id
        self.match_id=match_id
        self.message=message
        self.tick = tick
        super().__init__(id)
        
    def to_create() -> str:
        return """
            CREATE TABLE IF NOT EXISTS message (
                id uuid PRIMARY KEY,
                player_id VARCHAR(32) NOT NULL REFERENCES player(steam_id),
                round_id uuid NOT NULL REFERENCES round(id) ON DELETE CASCADE,
                match_id uuid NOT NULL REFERENCES match(id) ON DELETE CASCADE,
                message VARCHAR(255),
                tick int NOT NULL
            );
        """
    
class Grenade(DbClass):
    player_id: str
    team_id: UUID
    round_id: UUID
    match_id: UUID
    team: str
    grenade_type: str
    start_tick: int
    start_x: float
    start_y: float
    start_z: float
    start_zone: str
    end_tick: int
    end_x: float
    end_y: float
    end_z: float
    end_zone: str

    def __init__(
        self,
        player_id: str,
        team_id: UUID,
        round_id: UUID,
        match_id: UUID,
        team: str,
        grenade_type: str,
        start_tick: int,
        start_x: float,
        start_y: float,
        start_z: float,
        start_zone: str,
        end_tick: int,
        end_x: float,
        end_y: float,
        end_z: float,
        end_zone: str,
        id: Optional[UUID] = None,
    ) -> None:
        self.player_id = player_id
        self.team_id = team_id
        self.round_id = round_id
        self.match_id = match_id
        self.team = team
        self.grenade_type = grenade_type
        self.start_tick = start_tick
        self.start_x = start_x
        self.start_y = start_y
        self.start_z = start_z
        self.start_zone = start_zone
        self.end_tick = end_tick
        self.end_x = end_x
        self.end_y = end_y
        self.end_z = end_z
        self.end_zone = end_zone
        super().__init__(id)

    def to_create() -> str:
        return """
            CREATE TABLE IF NOT EXISTS grenade (
                id uuid PRIMARY KEY,
                player_id VARCHAR(32) NOT NULL REFERENCES player(steam_id),
                team_id uuid NOT NULL REFERENCES team(id),
                round_id uuid NOT NULL REFERENCES round(id) ON DELETE CASCADE,
                match_id uuid NOT NULL REFERENCES match(id) ON DELETE CASCADE,
                team VARCHAR(32) NOT NULL,
                grenade_type VARCHAR(32) NOT NULL,
                start_tick int NOT NULL,
                start_x float NOT NULL,
                start_y float NOT NULL,
                start_z float NOT NULL,
                start_zone VARCHAR(32),
                end_tick int NOT NULL,
                end_x float NOT NULL,
                end_y float NOT NULL,
                end_z float NOT NULL,
                end_zone VARCHAR(32)
            );
        """
    
class DbConnection:
    def __init__(self) -> None:
        # Enable UUIDS
        extras.register_uuid()

        self.__connection = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            database=os.getenv("POSTGRES_DATABASE"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
        )

        commands = [
            Team.to_create(),
            Player.to_create(),
            Match.to_create(),
            Round.to_create(),
            PlayerDefault.to_create(),
            Kill.to_create(),
            Buy.to_create(),
            Damage.to_create(),
            WeaponFire.to_create(),
            Grenade.to_create(),
            Message.to_create(),
            TournamentTeam.to_create(),
            Plant.to_create(),
        ]

        # Create tables if they don't exist
        with self.__connection.cursor() as cur:
            try:
                for command in commands:
                    cur.execute(command)
            except (psycopg2.DatabaseError, Exception) as error:
                print(error)

        self.__connection.commit()

    def __del__(self) -> None:
        self.__connection.close()

    def list_demos(self) -> List[str]:
        """
        Returns all filenames of the demos in the db
        """

        with self.__connection.cursor() as cur:
            cur.execute("SELECT file, tournament, id FROM match;")
            return cur.fetchall()
        
    def list_teams(self) -> List[str]:
        """
        Returns all names of teams in the db
        """

        with self.__connection.cursor() as cur:
            cur.execute("SELECT name, id FROM team;")
            return cur.fetchall()
        
    def list_players(self) -> List[str]:
        """
        Returns all steamids of players in the db
        """

        with self.__connection.cursor() as cur:
            cur.execute("SELECT name, steam_id, id FROM player;")
            return cur.fetchall()
        
    def list_rounds(self, match_id) -> List[Round]:
        """
        Returns all rounds in the match
        """

        with self.__connection.cursor() as cur:
            cur.execute(f"SELECT *, id FROM round WHERE round.match_id = '{match_id}'")
            data = cur.fetchall()
            return [Round(*x[1:]) for x in data]
        
    def get_team_id(self, team: str) -> UUID:
        """
        Returns the UUID of the team passed
        """

        with self.__connection.cursor() as cur:
            cur.execute("SELECT id FROM team WHERE name='{team}';".format(team=team))
            return cur.fetchall()[0][0]
        
    def get_player_id(self, steamid: str) -> UUID:
        """
        Returns the UUID of the player's steamid passed
        """

        with self.__connection.cursor() as cur:
            cur.execute("SELECT id FROM player WHERE steam_id='{steamid}';".format(steamid=steamid))
            return cur.fetchall()[0][0]    

    def insert(self, obj: DbClass) -> None:
        """
        Inserts a DbObject
        """

        with self.__connection.cursor() as cur:
            (query, args) = obj.to_insert()

            try:
                cur.execute(query, (args,))
            except Exception as error:
                print(error)

        self.__connection.commit()

    def insert_many(self, objs: List[DbClass]) -> None:
        """
        Inserts multiple DbObjects
        """
        if objs is None or len(objs) == 0: 
            return

        with self.__connection.cursor() as cur:
            (query, _) = objs[0].to_insert()
            data = [x.values() for x in objs]
            # print(query.as_string(cur) % data)
            try:
                extras.execute_values(cur, query, data)
            except Exception as error:
                print(error)
                print(traceback.format_exc())

        self.__connection.commit()
