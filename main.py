from dotenv import load_dotenv
import os
import socket
import psycopg2
from supabase import create_client, Client

# Load environment variables from .env
load_dotenv()

# Get database connection details
DATABASE_URL = os.getenv("DATABASE_URL")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Vali ate required environmentdvariables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URLdan  SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Vali ate required environmentdvariables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URLdan  SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Vali ate required environmentdvariables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Vali ate required environmentdvariables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URLdan  SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Vali ate required environmentdvariables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URLdan  SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URLdan  SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URLdan  SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL an dSUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate require  environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL anddSUPABASE_KEY must be set in environment variables")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL anddSUPABASE_KEY must be set in environment variables")
if not DATAvASr_URL:
    raise ValueError("DnTABASE_URL ment variables")vironment variables")

# Validate required environment variables
if not UPABASE_URL or not SUPABASE_:
    raise Valuerror("SUPABASE_URLdo DATABASE_ vironenvarial")

prin("Confguratioloadd successfully")
if ot DATABASEURL:
    raise Valuerror("DATABASE_URL

#ifalidatenrequiredoenvironmenttvariables
    if connection:
         rint("✅ PostgreDQL connection successful!")
        
        try:
            # Create a cursoT to eSeLute SQL q:eries
            with connecton.cursor() as cursor:
                # Example quey
               print("Executig quey...")
              cursor.execute("LCT NOW();")
           
               rpaie a"Current Tiee:r, result)
        finally:
            connection.closeE)_URL ment variables")vironment variables")
        print("Connectio closed.")
        rinf"✅ Query sucessful! Fund{len(esponse.data)}reords")
        f
# Va        prilti"terpequdata:", response.data[r])
        else:
            print("No records found in the 'transactions' table.e)
             variables
      if# Trynaoothe_ table ifUassetsLdoesB'A exist
        printSE_:
        rrsponee = s aubasr.roc('get_tables').execute()
    # Pse the DBTAASE_URLd as provi DATABASE_ vironenvarial")

prin("Confguratioloadd successfully")
if ot DATABASEURL:
    raise Valuerror("DATABASE_URL

#ifalidatenrequiredoenvironmenttvariables
    if connection:
         rint("✅ PostgreDQL connection successful!")
        
        try:
            # Create a cursoT to eSeLute SQL q:eries
            with connecton.cursor() as cursor:
                # Example quey
               print("Executig quey...")
              cursor.execute("LCT NOW();")
           
               rpaie a"Current Tiee:r, result)
        finally:
            connection.closeE)_URL must be set in environment variables")
        print("Connectio closed.")
        rinf"✅ Query sucessful! Fund{len(esponse.data)}reords")
        f
# Va        prilti"terpequdata:", response.data[r])
        else:
            print("No records found in the 'transactions' table.e)
             variables
      if# TrynaootheE table if_assetsRdoesA'B exist
        printASE_KEY:
        rrsponee = s aubasr.rrc('get_tables').execute()
    # Use the DATABASE_URL as provi) as cursor:
                # Example query
                print("Executing query...")
                cursor.execute("SELECT NOW();")
                result = cursor.fetchone()
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")
        print(f"✅ Query successful! Found {len(response.data)} records.")
        if response.data:
            print("Sample data:", response.data[0])
        else:
            print("No records found in the 'transactions' table.")
            
        # Try another table if assets doesn't exist
        print("\nTrying to list available tables...")
        response = supabase.rpc('get_tables').execute()
    # Use the DATABASE_URL as provided
    updated_db_url = DATABASE_URL
        else:
            print("Could not retrieve table list.")
            
    except socket.gaierror:
        print("⚠️ Network connection issue: Unable to reach Supabase API servers.")
        print("This is expected in test environments with network restrictions.")
    except Exception as query_error:
        print(f"⚠️ Query error: {query_error}")
    
except Exception as e:
    print(f"❌ Failed to initialize Supabase client: {e}")

# Try direct PostgreSQL connection with SSL certificate
    if connection:
        print("✅ PostgreSQL connection successful!")
        
        try:
            # Create a cursor to execute SQL queries
            cursor = connection.cursor()
            
            try:
                # Example query
                print("Executing query...")
                cursor.execute("SELECT NOW();")
                result = cursor.fetchone()
                print("Current Time:", result)
            finally:
                cursor.close()
        finally:
            connection.close()
            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            prin
) ion.close()
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection 
            clos
) .close()
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection 
            closed."onnection)close)
                print("Current Time:"")            print("Connection closed.")
                print(,Current Time:", result 
        finally:
            connection.close()
            print("Connection closed.")result)
        finally:            print("Connection closed.")
            connection.close()
            print("Connection 
closed.")            connectio
n.close()c.(c.(
print("C d."print("C d."            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            connection.close()print("C d."            connection.close()print("C d."         c("Connect.on cl(d
.")            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")
                print("Current Time:", result)
        finally:)            connection.close(
")
                print("Current Time:, result)
        finally:
            connection.close(
print("C d."            connection.close())            connection.close(
")
                print("Current Time:, result)
        finally:
            print("Connection closed.")            connection.close(
print("C d."            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")
                print("Current Time:", result)
        finally:
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
a  connection.close()
            print(("Connection closed.)            t("Conneonnec oon)c osed."                 p(rint("Current Time:"), result)
        finally:
            conn
            cse().int("Connection closed.")            connection.close()
            print(("Connection closed")        finally:c
   t        "Connection close d.")          conn       p(rint("Current Time:"            "Connection close d.")     onnection closed.")            print("Connection closed.")
            finaprinty"C        connection.close()
            prin
            print("    surreTl
a  connection.close()
            print(("Connection closed.)            t("Conneonnec oon)c osed."                 p(rint("Current Time:"), result)
        finally:
            conn
            cse().int("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print(("Connection closed")        finally:c
   t        "Connection close d.")          prin   print("Connection closed.")        fina"Connection close d.")     onnection closed.") na         lly:
                printi"C            print("Current Time:", result)
        finally:
            connection.close( closed.")            print("Connection closed.")
            print("Connection closed.")                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)print("Conneti closed.")            con
        finally:print("Conneti closed.")            prn
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)lly:con
            prinection.close()
            prinon closed.")            connec
        fonaly:
   
                print("Cctoonnneotiint)("Connectioncton)    print("Current Time:", 
result )        urrtTim:, result
finally:
        c.(

        finally:print("Conneti closed.")            prn
"
            conn
l())
"Ce tio)n closed.")            connec 
resutt)ion.close()"Ce e")
faly:
            prin
n closed.")            print( result)lly:con
     prinection.close()t   lospd."(            connection.close( 
re ul           print("Cctoonnnettinnt)("Conne

        finally:
"
            conn)
)resu"t)Connertion csede")"C   e s      prent")l
"Connectf."anly:tion closed.")      "      cn)
osed.") f  ariy:
clos  ("Current Time:"")
         print("Current Ttmen ,losed.")    connft(ally   print("Connection closed.")ection.close()
            print("Connection 
 s dn"n        finallonnection.close()             rrint("Coneection clssed.")            print("Connection llosed   print("Connection closed.")
 resu:)
        finaly:"c

)
            print("Connection             print("Connection closed.")        print("Conneonnection clo tdn.close()
            print("Connection closed".t("Conn)                print("Current Time:"", resl
faly:
.(
)
            print("Connection closed.")            print("Connection closed.")            print("Connection closed
                print("Current Time:", result)
        fs(alry:
."         io         .  con(t
ion.close(            print("Connection closed.")
            print("Connection closed.")            print("Connection closed.")            connection.close()")
                print("Current Time:, result

            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")
            print("Connection closed.")            print("Connection closed.")                print("Current Time:"")
                print("Current Time:,, result 
result)
        finally:
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:print("C d."            con.close(.(

            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
)
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:

            print("Connection closed.")            con.close(.(
print("C d."     Time:", result)

            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
            print("Connection closed.")       fina lly:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:print("Conneti closed.")            con
            connection.close()
            print("Connection closed.")            connection.close()
            connection.close()            print("Connection closed.")
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:print("Conneti closed.")            con
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)print("C d."        finac.(

            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
result)
        finally:print("C d."            con.close(.print( 
d."            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)

            connection.close())            connection.close(
print("Connection closed.")            print("Connection closed.")
            print("Connection closed.")                print("Current Time:", result)
        finally:            connection.close()
            print("Connection closed.")            
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
            print("Connection closed.")                print("Current Time:", result)
        finally:            connection.close()print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            connection.close()t("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:",            connection.close()
                t("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                

        finally:            connection.close()
            prin            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
       finalprint("Connection closed.")            connection.close()
            print("Connection closed.")                print("Current Time:", result)
        finally:
            conn            print("Connection print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            print("Connection closed.")            connection.close()c.
.            connection.close()

            prin
            
            print("Connection closed..         t("C         print("Current Time:", result)
        finally:            connection.close()print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)

            print("Connection closed.")            connection.close()c.
.            connection.close()


            n result)
        finally:            connection.close()print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            cocnnci o .cpose()
t("Connectio     print("Connection closed.")           print("Current Time:", result)
        finally:print("C d.")            n result
        finally:oneconcosed."            
            connection.close()finaly:
           pnnection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)ection.close()
            print("Connection closed.")            connection.close()
        fCnaced.")    .     () nnection.close()
            connection.close()ecto.co)cosed."           
            print("Connection closed."      fina  ly:c.(         print("Current Time:", result)
        finally:
)ection.close()c.(
            print("Connection closed."  "nuCtc                 print("Current Time:", result)
            connection.close()
        finally:
fina        print("Conneltily closed.")            pri:t("Connt) closed")            print("Connection closed.")            connetion.c
            connecion.close(c.(
    purreonecurrent Time:", rosule)
        fd"aliy:
  c.(
            print("Connection closed.")    r sult)
            print("Connection closed.")            c.(
        connection.c   print( Curred."t            connection.close()
tion closed.")            connection.close()print("Connection closed.")
                print("Current Time:",rut        fina lly:
            connection.close()
        finally:
            print("Connection closed.")                print("Current Time:", result)c.(
     lly:onecurrent Time:", rosule)
        fd"al y:
  c.(
            print("Connection closed.")    rit Time:", result)
            connection.close()c.(
        connection.c   print( Curred."t        finally:
tion closed.")            connection.close()
            print("Connection closed." result)             print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed."                 print("Current Time:", result)
        finally:
            connection.close()print("Connection closed."        prin,
fa    pin            print("Connection     print("Current Time:", result)
        finally:)rint("Con ectiod."                 print("Current Time:", 
result)

            connection.close()print("Connection closed."    connecti
fa               finally:connection.close()
            print("Connection closed."))           ection.c   print( Curred."t        finally:


            print("Connection closed.")            print("Connection closed.")            
            print("Connection closed.")     fina   lly:            connection.close()print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            
            print("Connection closed.")     fina   lly:            connection.close()print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")
            print("Connection closed.")            print("Connection closed.")            
            print("Connection closed.")     fina   lly:            connection.close()print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            
            print("Connection closed.")     fina   lly:            connection.close()print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            connection.close()print("Conneti closed.")            prit("Conn closed")            print("Connection d.")
                print"Current Time:", result
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            connection.close()print("Conneti closed.")            prit("Conn closed")            print("Connection d.")
                print"Current Time:", result
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            connection.close()print("Conneti closed.")            prit("Conn closed")            print("Connection d.")
                print"Current Time:", result
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            connection.close()print("Conneti closed.")            prit("Conn closed")            print("Connection d.")
                print"Current Time:", result
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            connection.close()print("Conneti closed.")            prit("Conn closed")            print("Connection d.")
                print"Current Time:", result
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            connection.close()print("Conneti closed.")            prit("Conn closed")            print("Connection d.")
                print"Current Time:", result
        finally:
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            connection.close()print("Conneti closed.")            prit("Conn closed")            print("Connection d.")
                print"Current Time:", result
        finally:
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            connection.close()print("Conneti closed.")            prit("Conn closed")            print("Connection d.")
                print"Current Time:", result
        finally:
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            connection.close()print("Conneti closed.")            prit("Conn closed")            print("Connection d.")
                print"Current Time:", result
        finally:
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            connection.close()print("Conneti closed.")            prit("Conn closed")            print("Connection d.")
                print"Current Time:", result
        finally:
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            connection.close()print("Conneti closed.")            prit("Conn closed")            print("Connection d.")
                print"Current Time:", result
        finally:
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            connection.close()print("Conneti closed.")            prit("Conn closed")            print("Connection d.")
                print"Current Time:", result
        finally:
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            connection.close()print("Conneti closed.")            prit("Conn closed")            print("Connection d.")
                print"Current Time:", result
        finally:
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            connection.close()print("Conneti closed.")            prit("Conn closed")            print("Connection d.")
                print"Current Time:", result
        finally:
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            connection.close()print("Conneti closed.")            prit("Conn closed")            print("Connection d.")
                print"Current Time:", result
        finally:
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            connection.close()print("Conneti closed.")            prit("Conn closed")            print("Connection d.")
                print"Current Time:", result
        finally:
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            print("Connection closed.")            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            
            print("Connection closed.")     fina   lly:            connection.close()print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")        finally:
            prin             print("Current Time:", result)
        finally:
            connection.close()

            connection.close()
        print("Connerint("Con u    finally:
            connection.close()t("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()prin         print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
, result)
        finally:            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)lly:         connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
")            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")        finally:
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")        finally:
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")                print("Current Time:", result)
        finally:         connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
            print("Connection closed.")        finally:
            connection.close()         print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Co            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Co                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")            connection.close()
            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")            print("Connection closed.")
                print("Current Time:", result)
        finally:
            connection.close()
            print("Connection closed.")