"""
Database connection module for the Financial Asset Relationship DB.
Supports both Supabase API and direct PostgreSQL connections.
"""

import logging
import os
from typing import Any, Dict, List

from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class DatabaseConnection:
    """Database connection handler that supports both Supabase and PostgreSQL"""

    def __init__(self) -> None:
        """Initialize the database connection"""
        self.supabase_client = None
        self.pg_conn = None
        self.connection_type = None

    def connect_supabase(self) -> bool:
        """Connect using Supabase client"""
        try:
            from supabase import Client, create_client

            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")

            if not supabase_url or not supabase_key:
                logger.error(
                    "Missing Supabase credentials. Please set SUPABASE_URL and SUPABASE_KEY environment variables."
                )
                return False

            self.supabase_client: Client = create_client(supabase_url, supabase_key)
            self.connection_type = "supabase"
            logger.info("Successfully connected to Supabase!")
            return True

        except ImportError:
            logger.warning("Supabase client not installed. Run 'pip install supabase'.")
            return False
        except Exception as e:
            logger.exception("Failed to connect to Supabase")
            return False

    def connect_postgres(self) -> bool:
        """Connect using direct PostgreSQL connection"""
        try:
            import psycopg2

            database_url = os.getenv("DATABASE_URL")

            if not database_url:
                logger.error("Missing DATABASE_URL environment variable.")
                return False

            self.pg_conn = psycopg2.connect(database_url)
            self.connection_type = "postgres"
            logger.info("Successfully connected to PostgreSQL database!")
            return True

        except ImportError:
            logger.warning("psycopg2 not installed. Run 'pip install psycopg2-binary'.")
            return False
        except Exception:
            logger.exception("Failed to connect to PostgreSQL database")
            return False

    def connect(self) -> bool:
        """Try to connect using available methods"""
        # Try Supabase first
        if self.connect_supabase():
            return True

        # Fall back to direct PostgreSQL
        logger.info("Falling back to direct PostgreSQL connection...")
        return self.connect_postgres()

    def query(self, table: str, select: str = "*", limit: int = 100) -> List[Dict[str, Any]]:
        """Query data from the database"""
        if not self.connection_type:
            if not self.connect():
                return []

        try:
            if self.connection_type == "supabase":
                response = self.supabase_client.table(table).select(select).limit(limit).execute()
                return response.data

            elif self.connection_type == "postgres":
                cursor = self.pg_conn.cursor()
                cursor.execute(f"SELECT {select} FROM {table} LIMIT {limit}")
                columns = [desc[0] for desc in cursor.description]
                results = []

                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))

                cursor.close()
                return results

        except Exception as e:
            logger.error(f"Query failed: {str(e)}")
            return []

    def close(self):
        """Close the database connection"""
        if self.connection_type == "postgres" and self.pg_conn:
            self.pg_conn.close()
            logger.info("PostgreSQL connection closed")

        self.connection_type = None
        self.supabase_client = None
        self.pg_conn = None


# Singleton instance
db = DatabaseConnection()


def get_db() -> DatabaseConnection:
    """Get the database connection singleton"""
    return db
