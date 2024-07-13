from cassandra.cluster import Session, ResultSet
from cassandra import ConsistencyLevel
from cassandra.query import SimpleStatement
from datetime import datetime
from enum import Enum
from pydantic import BaseModel
import logging
SOURCE_METADATA_TABLE = "meta_sources"
SIGNAL_METADATA_TABLE = "meta_signals"
SIGNAL_INSTANCE_PREFIX = "data_"

log = logging.getLogger()
class TSType(Enum):
    INT = "INT"
    FLOAT = "FLOAT"
    STRING = "STRING"
    
"""One singular datapoint"""
class TSPoint(BaseModel):
    timestamp:datetime
    value:int|float|str
"""A list of timeseries points of the same type"""
class Timeseries(BaseModel):
    datatype:TSType
    tsPoints:list[TSPoint]

"""A timeseries dataset container that resembles a singular timeseries like data of a single probe"""
class Signal(BaseModel):
    meta_info:str
    unique_name:str
    source_name:str

"""A device like a weather station"""
class Source(BaseModel):
    meta_info:str
    meta_zone:str
    unique_name:str

class Database:
    __keyspace_name__:str
    def __init__(self, keyspace_name:str):
        self.__keyspace_name__ = keyspace_name.lower()

    def ensure_database_structure(self, session:Session):
        log.info("Ensuring database keyspaces and meta tables.")
        resp:ResultSet = session.execute("""
            CREATE KEYSPACE IF NOT EXISTS %s
            WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': '1' }
            """ % self.__keyspace_name__)
        resp.all()
        session.set_keyspace(self.__keyspace_name__)
        session.execute("""
        CREATE TABLE IF NOT EXISTS %s (
            unique_name text,
            meta_info text,
            meta_zone text,
            PRIMARY KEY (unique_name)
        )
        """ % SOURCE_METADATA_TABLE)

        session.execute("""
        CREATE TABLE IF NOT EXISTS %s (
            name text,
            meta_info text,
            source_name text,
            PRIMARY KEY (name, source_name)
        )
        WITH CLUSTERING ORDER BY (source_name ASC)
        """ % SIGNAL_METADATA_TABLE)

        session.execute(f"CREATE INDEX IF NOT EXISTS ON {SIGNAL_METADATA_TABLE} (source_name)")
    
    def add_source(self, source:Source, session:Session):
        log.info("Adding source %s to database." % source.unique_name)
        query = SimpleStatement(f"INSERT INTO {SOURCE_METADATA_TABLE} (unique_name, meta_info, meta_zone) VALUES ( %s, %s, %s)", consistency_level=ConsistencyLevel.ONE)
        session.set_keyspace(self.__keyspace_name__)
        response = session.execute(query, (source.unique_name, source.meta_info, source.meta_zone))
        response.all()

    def add_signal(self, signal:Signal, session:Session):
        log.info("Adding signal %s to database." % signal.unique_name)
        query = SimpleStatement(f"INSERT INTO {SIGNAL_METADATA_TABLE} (name, meta_info, source_name) VALUES ( %s, %s, %s)", consistency_level=ConsistencyLevel.ONE)
        session.set_keyspace(self.__keyspace_name__)
        response = session.execute(query, (signal.unique_name, signal.meta_info, signal.source_name))
        response.all()

    def list_sources(self, session:Session) -> list:
        query = SimpleStatement(f"SELECT * FROM {SOURCE_METADATA_TABLE}", consistency_level=ConsistencyLevel.QUORUM);
        session.set_keyspace(self.__keyspace_name__)
        response:ResultSet = session.execute(query)
        rows = response.all()
        sources = list()
        for row_raw in rows:
            row = row_raw._asdict()
            sources.append(Source(unique_name=row["unique_name"], meta_info=row["meta_info"], meta_zone=row["meta_zone"]))
        return sources
    
    def list_signals(self, source_name, session:Session) -> list:
        query = SimpleStatement(f"SELECT * FROM {SIGNAL_METADATA_TABLE} where source_name='{source_name}'", consistency_level=ConsistencyLevel.QUORUM);
        session.set_keyspace(self.__keyspace_name__)
        response:ResultSet = session.execute(query)
        rows = response.all()
        signals = list()
        for row_raw in rows:
            row = row_raw._asdict()
            signals.append(Signal(unique_name=row['name'], meta_info=row['meta_info'], source_name=row['source_name'])) 
        return signals
    def write_timeseries(self, source_name:str, signal_name:str, timeseries:Timeseries, session:Session):
        log.info(f"Writing timeseries {signal_name} from source {source_name} to database.")
        tablename = f"{SIGNAL_INSTANCE_PREFIX}{source_name.lower().replace('_','')}_{signal_name.lower().replace('_','')}"
        session.set_keyspace(self.__keyspace_name__)
        session.execute("""
        CREATE TABLE IF NOT EXISTS %s (
            event_time timestamp,
            date date, 
            value_int int,
            value_float float,
            value_text text,
            PRIMARY KEY (date, event_time)
        ) WITH CLUSTERING ORDER BY (event_time DESC);
        """ % tablename)
        query = SimpleStatement(f"INSERT INTO {tablename} (event_time, date, value_int, value_float, value_text) VALUES ( %s, %s, %s, %s, %s)", consistency_level=ConsistencyLevel.ONE)
        for t_point in timeseries.tsPoints:
            event_date = t_point.timestamp.date()
            v_int = None
            v_float = None
            v_text = None
            if(timeseries.datatype == TSType.INT):
                v_int = t_point.value
            elif(timeseries.datatype == TSType.FLOAT):
                v_float = t_point.value
            else:
                v_text = t_point.value
            response = session.execute(query, (t_point.timestamp, event_date, v_int, v_float, v_text))