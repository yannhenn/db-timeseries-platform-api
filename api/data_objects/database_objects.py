from cassandra.cluster import Session, ResultSet
from cassandra import ConsistencyLevel
from cassandra.query import SimpleStatement
from datetime import datetime
from enum import Enum
import logging
SOURCE_METADATA_TABLE = "meta_sources"
SIGNAL_METADATA_TABLE = "meta_signals"
SIGNAL_INSTANCE_PREFIX = "data_"

log = logging.getLogger()
class TSType(Enum):
    FLOAT = 1
    STRING = 2
    INT = 3
"""One singular datapoint"""
class TSPoint:
    timestamp:datetime
    value:any
"""A list of timeseries of the same type"""
class Timeseries:
    datatype:TSType
    TSPoints:list[TSPoint]

"""A timeseries dataset container that resembles a singular timeseries like data of a single probe"""
class Signal:
    meta_info:str
    unique_name:str
    timeseries_data:Timeseries
    def __init__(self):
        pass

"""A device like a weather station"""
class Source:
    meta_info:str
    unique_name:str
    signals:Signal
    def __init__(self):
        pass

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
        resp.all
        session.set_keyspace(self.__keyspace_name__)
        session.execute("""
        CREATE TABLE IF NOT EXISTS %s (
            unique_name text,
            meta_info text,
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
        """ % SIGNAL_METADATA_TABLE)
    
    def add_source(self, source:Source, session:Session):
        log.info("Adding source %s to database." % source.unique_name)
        query = SimpleStatement("""
            INSERT INTO % (unique_name, meta_info)
            VALUES ( ?, ?)
            """ % SOURCE_METADATA_TABLE, consistency_level=ConsistencyLevel.ONE)
        response = session.execute(query, (source.unique_name, source.meta_info))
        response.all()

    def add_signal(self, source_name:str, signal:Signal, session:Session):
        log.info("Adding signal %s to database." % signal.name)
        query = SimpleStatement("""
            INSERT INTO % (name, meta_info, source_name)
            VALUES ( ?, ?, ?)
            """ % SIGNAL_METADATA_TABLE, consistency_level=ConsistencyLevel.ONE)
        response = session.execute(query, (signal.unique_name, signal.meta_info, source_name))

    def get_sources(self, session:Session) -> list:
        pass
