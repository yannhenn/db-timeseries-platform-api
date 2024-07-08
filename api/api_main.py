from fastapi import FastAPI, Depends, HTTPException
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster, Session, ResultSet
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement
import uvicorn, dotenv, os, jwt, typing
from data_objects.database_objects import Database


#Env var loading
dotenv.load_dotenv()
cluster_addrs = os.environ.get("CASSANDRA_URLS").split(",")
JWT_SECRET = os.environ.get("JWT_SECRET")
CASSANDRA_PORT = os.environ.get("CASSANDRA_PORT")
CASSANDRA_KEYSPACE = os.environ.get("CASSANDRA_KEYSPACE")

app = FastAPI()
security = HTTPBearer
database = Database(keyspace_name=CASSANDRA_KEYSPACE)
"""
Returns the JWT subtoken
"""
def get_jwt_token_up(user:str, password:str):
    token = jwt.encode({"username": user, "password": password}, JWT_SECRET, algorithm="HS256")
    return token

"""
Returns a dict with the keys "user","password"
"""
def get_up_from_jwt_token(jwt_token:str):
    return jwt.decode(jwt_token, JWT_SECRET, algorithms=["HS256"])



async def get_token_from_requests(auth: typing.Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> str:
    if auth is None:
        raise HTTPException(status_code=401, detail="No token provided")
    else:
        token = auth.credentials
        return token
"""
This function returns a new DB session with the supplied 
credentials
 """
def get_db_session_atomic(username, password) -> Session:
    cluster = Cluster(contact_points=cluster_addrs, port = CASSANDRA_PORT)
    auth_provider = PlainTextAuthProvider(username=username, password=password)
    cluster.auth_provider = auth_provider
    return cluster.connect()

@app.get("/")
def get_root():
    return "Hello to IoT API"

@app.get("/getToken")
def get_root(username: str, password: str):
    if (username==None or password == None):
        raise HTTPException(status_code=400, detail="No username/password provided!")
    else:
        try:
            session = get_db_session_atomic(username,password)
        except:
            raise HTTPException(status_code=401, detail="Invalid username/password!")
        return get_jwt_token_up(username, password)

@app.get("/keyspaces")
def get_keyspaces(token: str = Depends(get_token_from_requests)):
    authdict = get_up_from_jwt_token(token)
    session:Session = get_db_session_atomic(authdict['username'], authdict['password'])
    query = SimpleStatement("""
        DESCRIBE KEYSPACES;
        """, consistency_level=ConsistencyLevel.ONE)
    
    query_result:ResultSet = session.execute(query)
    all_keyspaces = list(query_result)
    return all_keyspaces

def get_all_signals(sourceID:str, token: str = Depends(get_token_from_requests)):
    pass
def get_all_sources(token: str = Depends(get_token_from_requests)):
    pass

def main():
    database.ensure_database_structure(get_db_session_atomic(os.environ.get("CASSANDRA_USERNAME"), os.environ.get("CASSANDRA_PASSWORD")))
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("API_PORT")))

if(__name__ == '__main__'):
    main()