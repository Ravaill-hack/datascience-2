import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv("secrets")

postgres_db = os.environ["POSTGRES_DB"]
postgres_user = os.environ["POSTGRES_USER"]
postgres_password = os.environ["POSTGRES_PASSWORD"]

db = create_engine(f"postgresql://{postgres_user}:{postgres_password}@localhost:5432/{postgres_db}")
