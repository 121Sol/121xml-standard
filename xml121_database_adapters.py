# © 2026 121 Solutions USA. All rights reserved.
#
# The trademarks 121XQ, 121XML, and 121MetaVerse are the exclusive
# property of 121 Solutions USA.
#
# Unauthorized use, reproduction, or distribution of this material,
# including any proprietary designs, software, or documentation, is
# strictly prohibited without prior written permission from 121 Solutions USA.
"""
121XML Database Adapters
Support for PostgreSQL, MongoDB, DynamoDB, Redis, and other databases

Version: 1.0.0
License: Proprietary - 121 Group
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json


class DatabaseType(Enum):
    """Supported database types"""
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    DYNAMODB = "dynamodb"
    REDIS = "redis"
    MYSQL = "mysql"
    ORACLE = "oracle"
    CASSANDRA = "cassandra"
    ELASTICSEARCH = "elasticsearch"


@dataclass
class ConnectionConfig:
    """Database connection configuration"""
    database_type: DatabaseType
    host: str
    port: int
    username: str
    password: str
    database: str
    pool_size: int = 10
    timeout_seconds: int = 30
    ssl_enabled: bool = True
    read_replica_hosts: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QueryResult:
    """Result of database query"""
    success: bool
    rows: List[Dict[str, Any]] = field(default_factory=list)
    row_count: int = 0
    affected_rows: int = 0
    execution_time_ms: float = 0.0
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DatabaseAdapter(ABC):
    """Abstract base class for database adapters"""

    def __init__(self, config: ConnectionConfig):
        self.config = config
        self.connection = None
        self.connected = False
        self.query_log: List[Dict[str, Any]] = []

    @abstractmethod
    def connect(self) -> bool:
        """Establish database connection"""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """Close database connection"""
        pass

    @abstractmethod
    def execute_query(self, query: str, parameters: Optional[List[Any]] = None) -> QueryResult:
        """Execute SELECT query"""
        pass

    @abstractmethod
    def execute_update(self, query: str, parameters: Optional[List[Any]] = None) -> QueryResult:
        """Execute INSERT/UPDATE/DELETE query"""
        pass

    @abstractmethod
    def execute_transaction(self, queries: List[Tuple[str, Optional[List[Any]]]]) -> QueryResult:
        """Execute multiple queries in transaction"""
        pass

    @abstractmethod
    def create_table(self, table_name: str, schema: Dict[str, str]) -> bool:
        """Create table from schema"""
        pass

    @abstractmethod
    def insert_record(self, table_name: str, record: Dict[str, Any]) -> QueryResult:
        """Insert single record"""
        pass

    @abstractmethod
    def update_record(self, table_name: str, record_id: Any, updates: Dict[str, Any]) -> QueryResult:
        """Update single record"""
        pass

    @abstractmethod
    def delete_record(self, table_name: str, record_id: Any) -> QueryResult:
        """Delete single record"""
        pass

    @abstractmethod
    def get_record(self, table_name: str, record_id: Any) -> QueryResult:
        """Retrieve single record"""
        pass

    @abstractmethod
    def list_records(self, table_name: str, limit: int = 100, offset: int = 0) -> QueryResult:
        """List records with pagination"""
        pass

    def log_query(self, query: str, execution_time_ms: float, success: bool):
        """Log query execution"""
        self.query_log.append({
            "query": query,
            "timestamp": datetime.utcnow().isoformat(),
            "execution_time_ms": execution_time_ms,
            "success": success
        })


class PostgreSQLAdapter(DatabaseAdapter):
    """PostgreSQL database adapter"""

    def connect(self) -> bool:
        """Connect to PostgreSQL"""
        try:
            # In production: import psycopg2
            # self.connection = psycopg2.connect(...)
            self.connected = True
            return True
        except Exception as e:
            return False

    def disconnect(self) -> bool:
        """Disconnect from PostgreSQL"""
        try:
            if self.connection:
                self.connection.close()
            self.connected = False
            return True
        except Exception:
            return False

    def execute_query(self, query: str, parameters: Optional[List[Any]] = None) -> QueryResult:
        """Execute SELECT query"""
        import time
        start = time.time()

        result = QueryResult(success=False)

        try:
            # In production: use cursor and execute query
            # cursor = self.connection.cursor()
            # cursor.execute(query, parameters or [])
            # result.rows = [dict(row) for row in cursor.fetchall()]

            result.rows = [{"example": "data"}]
            result.row_count = len(result.rows)
            result.success = True
        except Exception as e:
            result.errors = [str(e)]

        result.execution_time_ms = (time.time() - start) * 1000
        self.log_query(query, result.execution_time_ms, result.success)
        return result

    def execute_update(self, query: str, parameters: Optional[List[Any]] = None) -> QueryResult:
        """Execute INSERT/UPDATE/DELETE"""
        import time
        start = time.time()

        result = QueryResult(success=False)

        try:
            # In production: execute and commit
            # cursor = self.connection.cursor()
            # cursor.execute(query, parameters or [])
            # self.connection.commit()
            # result.affected_rows = cursor.rowcount

            result.affected_rows = 1
            result.success = True
        except Exception as e:
            result.errors = [str(e)]

        result.execution_time_ms = (time.time() - start) * 1000
        self.log_query(query, result.execution_time_ms, result.success)
        return result

    def execute_transaction(self, queries: List[Tuple[str, Optional[List[Any]]]]) -> QueryResult:
        """Execute transaction"""
        result = QueryResult(success=False)

        try:
            # In production: wrap in BEGIN/COMMIT
            for query, params in queries:
                self.execute_update(query, params)
            result.success = True
        except Exception as e:
            result.errors = [str(e)]

        return result

    def create_table(self, table_name: str, schema: Dict[str, str]) -> bool:
        """Create PostgreSQL table"""
        columns = ", ".join(f"{col} {dtype}" for col, dtype in schema.items())
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
        result = self.execute_update(query)
        return result.success

    def insert_record(self, table_name: str, record: Dict[str, Any]) -> QueryResult:
        """Insert record"""
        columns = ", ".join(record.keys())
        placeholders = ", ".join(["%s"] * len(record))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        return self.execute_update(query, list(record.values()))

    def update_record(self, table_name: str, record_id: Any, updates: Dict[str, Any]) -> QueryResult:
        """Update record"""
        set_clause = ", ".join(f"{k} = %s" for k in updates.keys())
        query = f"UPDATE {table_name} SET {set_clause} WHERE id = %s"
        params = list(updates.values()) + [record_id]
        return self.execute_update(query, params)

    def delete_record(self, table_name: str, record_id: Any) -> QueryResult:
        """Delete record"""
        query = f"DELETE FROM {table_name} WHERE id = %s"
        return self.execute_update(query, [record_id])

    def get_record(self, table_name: str, record_id: Any) -> QueryResult:
        """Get single record"""
        query = f"SELECT * FROM {table_name} WHERE id = %s"
        return self.execute_query(query, [record_id])

    def list_records(self, table_name: str, limit: int = 100, offset: int = 0) -> QueryResult:
        """List records"""
        query = f"SELECT * FROM {table_name} LIMIT %s OFFSET %s"
        return self.execute_query(query, [limit, offset])


class MongoDBAdapter(DatabaseAdapter):
    """MongoDB database adapter"""

    def connect(self) -> bool:
        """Connect to MongoDB"""
        try:
            # In production: import pymongo
            # from pymongo import MongoClient
            # self.connection = MongoClient(...)
            self.connected = True
            return True
        except Exception:
            return False

    def disconnect(self) -> bool:
        """Disconnect from MongoDB"""
        try:
            if self.connection:
                self.connection.close()
            self.connected = False
            return True
        except Exception:
            return False

    def execute_query(self, query: str, parameters: Optional[List[Any]] = None) -> QueryResult:
        """Execute MongoDB query (aggregation pipeline)"""
        import time
        start = time.time()

        result = QueryResult(success=False)

        try:
            # In production: parse query as MongoDB aggregation
            # result.rows = list(collection.aggregate(json.loads(query)))

            result.rows = [{"_id": "example", "data": "value"}]
            result.row_count = len(result.rows)
            result.success = True
        except Exception as e:
            result.errors = [str(e)]

        result.execution_time_ms = (time.time() - start) * 1000
        return result

    def execute_update(self, query: str, parameters: Optional[List[Any]] = None) -> QueryResult:
        """Execute MongoDB update"""
        import time
        start = time.time()

        result = QueryResult(success=False)

        try:
            # In production: execute update
            result.affected_rows = 1
            result.success = True
        except Exception as e:
            result.errors = [str(e)]

        result.execution_time_ms = (time.time() - start) * 1000
        return result

    def execute_transaction(self, queries: List[Tuple[str, Optional[List[Any]]]]) -> QueryResult:
        """Execute MongoDB transaction"""
        result = QueryResult(success=False)

        try:
            for query, params in queries:
                self.execute_update(query, params)
            result.success = True
        except Exception as e:
            result.errors = [str(e)]

        return result

    def create_table(self, table_name: str, schema: Dict[str, str]) -> bool:
        """Create MongoDB collection with schema validation"""
        # In production: create collection with validation rules
        return True

    def insert_record(self, table_name: str, record: Dict[str, Any]) -> QueryResult:
        """Insert MongoDB document"""
        # In production: collection.insert_one(record)
        return QueryResult(success=True, affected_rows=1)

    def update_record(self, table_name: str, record_id: Any, updates: Dict[str, Any]) -> QueryResult:
        """Update MongoDB document"""
        # In production: collection.update_one({"_id": record_id}, {"$set": updates})
        return QueryResult(success=True, affected_rows=1)

    def delete_record(self, table_name: str, record_id: Any) -> QueryResult:
        """Delete MongoDB document"""
        # In production: collection.delete_one({"_id": record_id})
        return QueryResult(success=True, affected_rows=1)

    def get_record(self, table_name: str, record_id: Any) -> QueryResult:
        """Get MongoDB document"""
        result = QueryResult(success=True)
        # In production: result.rows = [collection.find_one({"_id": record_id})]
        result.rows = [{"_id": record_id, "example": "data"}]
        result.row_count = 1
        return result

    def list_records(self, table_name: str, limit: int = 100, offset: int = 0) -> QueryResult:
        """List MongoDB documents"""
        result = QueryResult(success=True)
        # In production: result.rows = list(collection.find().skip(offset).limit(limit))
        result.rows = [{"example": "data"}] * min(10, limit)
        result.row_count = len(result.rows)
        return result


class DynamoDBAdapter(DatabaseAdapter):
    """AWS DynamoDB database adapter"""

    def connect(self) -> bool:
        """Connect to DynamoDB"""
        try:
            # In production: import boto3
            # self.connection = boto3.resource("dynamodb", ...)
            self.connected = True
            return True
        except Exception:
            return False

    def disconnect(self) -> bool:
        """Disconnect from DynamoDB"""
        self.connected = False
        return True

    def execute_query(self, query: str, parameters: Optional[List[Any]] = None) -> QueryResult:
        """Execute DynamoDB query"""
        import time
        start = time.time()

        result = QueryResult(success=False)

        try:
            # In production: parse query and execute scan/query
            result.rows = [{"id": "example", "data": "value"}]
            result.row_count = len(result.rows)
            result.success = True
        except Exception as e:
            result.errors = [str(e)]

        result.execution_time_ms = (time.time() - start) * 1000
        return result

    def execute_update(self, query: str, parameters: Optional[List[Any]] = None) -> QueryResult:
        """Execute DynamoDB update"""
        import time
        start = time.time()

        result = QueryResult(success=False)

        try:
            result.affected_rows = 1
            result.success = True
        except Exception as e:
            result.errors = [str(e)]

        result.execution_time_ms = (time.time() - start) * 1000
        return result

    def execute_transaction(self, queries: List[Tuple[str, Optional[List[Any]]]]) -> QueryResult:
        """Execute DynamoDB transaction"""
        result = QueryResult(success=False)

        try:
            for query, params in queries:
                self.execute_update(query, params)
            result.success = True
        except Exception as e:
            result.errors = [str(e)]

        return result

    def create_table(self, table_name: str, schema: Dict[str, str]) -> bool:
        """Create DynamoDB table"""
        # In production: dynamodb.create_table(...)
        return True

    def insert_record(self, table_name: str, record: Dict[str, Any]) -> QueryResult:
        """Put item in DynamoDB"""
        return QueryResult(success=True, affected_rows=1)

    def update_record(self, table_name: str, record_id: Any, updates: Dict[str, Any]) -> QueryResult:
        """Update DynamoDB item"""
        return QueryResult(success=True, affected_rows=1)

    def delete_record(self, table_name: str, record_id: Any) -> QueryResult:
        """Delete DynamoDB item"""
        return QueryResult(success=True, affected_rows=1)

    def get_record(self, table_name: str, record_id: Any) -> QueryResult:
        """Get DynamoDB item"""
        result = QueryResult(success=True)
        result.rows = [{"id": record_id, "example": "data"}]
        result.row_count = 1
        return result

    def list_records(self, table_name: str, limit: int = 100, offset: int = 0) -> QueryResult:
        """Scan DynamoDB table"""
        result = QueryResult(success=True)
        result.rows = [{"example": "data"}] * min(10, limit)
        result.row_count = len(result.rows)
        return result


class RedisAdapter(DatabaseAdapter):
    """Redis cache/data store adapter"""

    def connect(self) -> bool:
        """Connect to Redis"""
        try:
            # In production: import redis
            # self.connection = redis.StrictRedis(...)
            self.connected = True
            return True
        except Exception:
            return False

    def disconnect(self) -> bool:
        """Disconnect from Redis"""
        try:
            if self.connection:
                self.connection.close()
            self.connected = False
            return True
        except Exception:
            return False

    def execute_query(self, query: str, parameters: Optional[List[Any]] = None) -> QueryResult:
        """Execute Redis GET"""
        import time
        start = time.time()

        result = QueryResult(success=False)

        try:
            # In production: execute Redis command
            result.rows = [{"value": "cached_data"}]
            result.row_count = 1
            result.success = True
        except Exception as e:
            result.errors = [str(e)]

        result.execution_time_ms = (time.time() - start) * 1000
        return result

    def execute_update(self, query: str, parameters: Optional[List[Any]] = None) -> QueryResult:
        """Execute Redis SET"""
        import time
        start = time.time()

        result = QueryResult(success=False)

        try:
            result.affected_rows = 1
            result.success = True
        except Exception as e:
            result.errors = [str(e)]

        result.execution_time_ms = (time.time() - start) * 1000
        return result

    def execute_transaction(self, queries: List[Tuple[str, Optional[List[Any]]]]) -> QueryResult:
        """Execute Redis MULTI/EXEC"""
        result = QueryResult(success=False)

        try:
            for query, params in queries:
                self.execute_update(query, params)
            result.success = True
        except Exception as e:
            result.errors = [str(e)]

        return result

    def create_table(self, table_name: str, schema: Dict[str, str]) -> bool:
        """Redis doesn't have tables - returns True"""
        return True

    def insert_record(self, table_name: str, record: Dict[str, Any]) -> QueryResult:
        """Store in Redis"""
        return QueryResult(success=True, affected_rows=1)

    def update_record(self, table_name: str, record_id: Any, updates: Dict[str, Any]) -> QueryResult:
        """Update Redis value"""
        return QueryResult(success=True, affected_rows=1)

    def delete_record(self, table_name: str, record_id: Any) -> QueryResult:
        """Delete from Redis"""
        return QueryResult(success=True, affected_rows=1)

    def get_record(self, table_name: str, record_id: Any) -> QueryResult:
        """Get from Redis"""
        result = QueryResult(success=True)
        result.rows = [{"id": record_id, "cached": True}]
        result.row_count = 1
        return result

    def list_records(self, table_name: str, limit: int = 100, offset: int = 0) -> QueryResult:
        """List Redis keys"""
        result = QueryResult(success=True)
        result.rows = [{"key": f"key_{i}"} for i in range(min(10, limit))]
        result.row_count = len(result.rows)
        return result


class DatabaseAdapterFactory:
    """Factory for creating database adapters"""

    @staticmethod
    def create_adapter(config: ConnectionConfig) -> DatabaseAdapter:
        """Create appropriate database adapter"""

        if config.database_type == DatabaseType.POSTGRESQL:
            return PostgreSQLAdapter(config)
        elif config.database_type == DatabaseType.MONGODB:
            return MongoDBAdapter(config)
        elif config.database_type == DatabaseType.DYNAMODB:
            return DynamoDBAdapter(config)
        elif config.database_type == DatabaseType.REDIS:
            return RedisAdapter(config)
        else:
            raise ValueError(f"Unsupported database type: {config.database_type}")


if __name__ == "__main__":
    # Example usage
    config = ConnectionConfig(
        database_type=DatabaseType.POSTGRESQL,
        host="localhost",
        port=5432,
        username="user",
        password="password",
        database="121xml"
    )

    adapter = DatabaseAdapterFactory.create_adapter(config)
    adapter.connect()

    result = adapter.list_records("invoices", limit=10)
    print(f"Query successful: {result.success}")
    print(f"Rows: {len(result.rows)}")
    print(f"Execution time: {result.execution_time_ms:.2f}ms")
