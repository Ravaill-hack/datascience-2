import os

import matplotlib.pyplot as plt
import pandas as pd
from dotenv import load_dotenv
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sqlalchemy import create_engine

load_dotenv("secrets")

db = create_engine(
    f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}"
    f"@localhost:5432/{os.environ['POSTGRES_DB']}"
)

plt.style.use("seaborn-v0_8-darkgrid")

# Variables RFM par client : Recency, Frequency, Monetary
query = """
SELECT user_id,
       COUNT(*)        AS frequency,
       SUM(price)      AS monetary,
       MAX(event_time) AS last_purchase
FROM customers
WHERE event_type = 'purchase'
  AND event_time >= '2022-10-01'
  AND event_time <  '2023-03-01'
GROUP BY user_id
"""
df = pd.read_sql(query, db)
df["last_purchase"] = pd.to_datetime(df["last_purchase"]).dt.tz_localize(None)
today = df["last_purchase"].max()
df["recency"] = (today - df["last_purchase"]).dt.days

# Les variables sont mises à l'échelle pour que KMeans ne soit pas
# dominé par celle qui a les plus grandes valeurs
X = StandardScaler().fit_transform(df[["recency", "frequency", "monetary"]])

# Méthode du coude : inertie pour k = 1..10
inertias = []
ks = range(1, 11)
for k in ks:
    km = KMeans(n_clusters=k, n_init=10, random_state=42)
    km.fit(X)
    inertias.append(km.inertia_)

plt.figure(figsize=(8, 5))
plt.plot(list(ks), inertias)
plt.title("The Elbow Method")
plt.xlabel("Number of clusters")
plt.show()
