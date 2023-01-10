from .logger import log
import sqlite3
import copy
import time

class SQLite3(object):
    blocked = False
    
    """ DataBase Class """

    def __init__(self, database=":memory:", host="localhost", user=None, password=None, max_idle_time=7*3600):
        self.host = host
        self.database = database
        self.max_idle_time = max_idle_time

        args = dict(db=database)
        self._db = None
        self._db_args = args
        self._last_use_time = time.time()
        try:
            self.reconnect()
        except:
            log.error("Cannot connect to Sqlite3 on %s", self.host, exc_info=True)

    def __del__(self):
        self.close()

    def cursor(self):
        return self._cursor

    def close(self):
        """Closes this database connection."""
        if getattr(self, "_db", None) is not None:
            self._db.close()
            self._db = None

    def reconnect(self):
        """Closes the existing database connection and re-opens it."""
        self.close()
        self._db = sqlite3.connect(self.database,check_same_thread = False)
        self.isolation_level = None    # similar to mysql self._db.autocommit(True)

    def iter(self, query, *parameters):
        """Returns an iterator for the given query and parameters."""
        self._db = sqlite3.connect(self.database,check_same_thread = False)
        self._ensure_connected()
        cursor = self._cursor()
        try:
            self._execute(cursor, query, parameters)
            column_names = [d[0] for d in cursor.description]
            for row in cursor:
                yield Row(zip(column_names, row))
        finally:
            cursor.close()

    def query(self, query, *parameters):
        """Returns a row list for the given query and parameters."""
        self._db = sqlite3.connect(self.database,check_same_thread = False)
        cursor = self._cursor()
        try:
            self._execute(cursor, query, parameters)
            column_names = [d[0] for d in cursor.description]
            return [Row(zip(column_names, row)) for row in cursor]
        finally:
            pass  # cursor.close()

    def get(self, query, *parameters):
        """Returns the first row returned for the given query."""
        rows = self.query(query, *parameters)
        if not rows:
            return None
        elif len(rows) > 1:
            log.error("Multiple rows returned for Database.get() query")
            raise
        else:
            return rows[0]

    def execute(self, query, *parameters):
        """Executes the given query, returning the lastrowid from the query."""
        while self.blocked: continue
        
        self.blocked=True
        self._db = sqlite3.connect(self.database,check_same_thread = False)
        cursor = self._cursor()
        try:
            self._execute(cursor, query, parameters)
            return cursor.lastrowid
        finally:
            cursor.close()
            self.blocked=False

    def executemany(self, query, parameters):
        """Executes the given query against all the given param sequences.
        We return the lastrowid from the query.
        """
        while self.blocked: continue
        
        self.blocked=True
        self._db = sqlite3.connect(self.database,check_same_thread = False)
        cursor = self._cursor()
        try:
            cursor.executemany(query, parameters)
            self._db.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
            self.blocked=False

    def _ensure_connected(self):
        # if  coonection has been idle for too long (7 hours by default).
        # pre-emptive
        if (self._db is None or
            (time.time() - self._last_use_time > self.max_idle_time)):
            self.reconnect()
        self._last_use_time = time.time()

    def _cursor(self):
        self._ensure_connected()
        return self._db.cursor()

    def _execute(self, cursor, query, parameters):
        try:
            cursor.execute(query, parameters)
            self._db.commit()
            return
        except OperationalError:
            log.error("Error connecting to SQLite3 on %s", self.host)
#            self.close()
            raise
    
    def initDatabase(self, filename):
        c = self._cursor()
        with open(filename, 'r') as f:
            buildUpQuery = f.read()
            c.executescript(buildUpQuery)


class Row(dict):
    """A dict that allows for object-like property access syntax."""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

# Alias some common Sqlite3 exceptions
IntegrityError = sqlite3.IntegrityError
OperationalError = sqlite3.OperationalError
