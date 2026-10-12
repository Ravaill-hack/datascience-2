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

query = """
SELECT event_type, COUNT(*) AS count
FROM customers
GROUP BY event_type
"""

df = pd.read_sql(query, db)

plt.figure(figsize=(8, 8))
plt.pie(df["count"], labels=df["event_type"], autopct="%1.1f%%")
plt.show()
