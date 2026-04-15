import logging
import asyncpg

from ....core.config import Configuration

logger = logging.getLogger("virel.core.services.postgres")

class PostgresClient:
    """
    A client for interacting with a PostgreSQL database using asyncpg. This class
    manages a connection pool and provides convenience methods for executing
    queries and fetching results from the database asynchronously.
    """
    
    def __init__(self):
        """
        Initializes the PostgresClient instance by setting the connection pool
        attribute to None. The actual connection pool will be created when
        connect() is called.
        """
        self.pool: asyncpg.Pool | None = None

    async def connect(self):
        """
        Connects to the PostgreSQL database by creating a connection pool using
        asyncpg's create_pool method with the DSN provided in the configuration.
        """

        self.pool = await asyncpg.create_pool(
            dsn=Configuration.Core.postgres_url,
            min_size=1,
            max_size=10,
        )
        logger.info("Connected to PostgreSQL")

    async def close(self):
        """
        Closes the PostgreSQL connection pool if it exists.
        """

        if self.pool:
            await self.pool.close()
            logger.info("Closed PostgreSQL connection pool")

    async def execute(self, query: str, *args):
        """
        Executes a query against the PostgreSQL database using the connection pool.
        This is typically used for queries that do not return results, such as
        INSERT, UPDATE, or DELETE statements.

        Args:
            query (str): The SQL query to execute.
            *args: Arguments to pass to the query placeholders.

        Returns:
            The result of the execution as returned by asyncpg's execute method.
        """
        
        return await self.pool.execute(query, *args)

    async def fetch(self, query: str, *args):
        """
        Executes a query against the PostgreSQL database using the connection pool
        and returns all resulting rows. This is typically used for SELECT queries
        that return multiple rows.

        Args:
            query (str): The SQL query to execute.
            *args: Arguments to pass to the query placeholders.

        Returns:
            A list of records as returned by asyncpg's fetch method.
        """

        return await self.pool.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        """
        Executes a query against the PostgreSQL database using the connection pool
        and returns a single row. This is typically used for SELECT queries that
        are expected to return only one row.

        Args:
            query (str): The SQL query to execute.
            *args: Arguments to pass to the query placeholders.

        Returns:
            A single record as returned by asyncpg's fetchrow method.
        """

        return await self.pool.fetchrow(query, *args)

    async def fetchval(self, query: str, *args):
        """
        Executes a query against the PostgreSQL database using the connection pool
        and returns a single value. This is typically used for SELECT queries that
        return a single scalar value, such as COUNT(*) or retrieving a single column
        from a single row.

        Args:
            query (str): The SQL query to execute.
            *args: Arguments to pass to the query placeholders.

        Returns:
            The value of the first column of the first row as returned by asyncpg's fetchval method.
        """

        return await self.pool.fetchval(query, *args)
