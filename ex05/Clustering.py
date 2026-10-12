import os

import matplotlib.pyplot as plt
import numpy as np
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

query = """
SELECT user_id,
       COUNT(*)        AS frequency,
       SUM(price)      AS monetary,
       MIN(event_time) AS first_purchase,
       MAX(event_time) AS last_purchase
FROM customers
WHERE event_type = 'purchase'
  AND event_time >= '2022-10-01'
  AND event_time <  '2023-03-01'
GROUP BY user_id
"""
df = pd.read_sql(query, db)
for col in ("first_purchase", "last_purchase"):
    df[col] = pd.to_datetime(df[col]).dt.tz_localize(None)

today = df["last_purchase"].max()
df["recency"] = (today - df["last_purchase"]).dt.days 
df["tenure"] = (today - df["first_purchase"]).dt.days

features = ["recency", "frequency", "monetary", "tenure"]
X = StandardScaler().fit_transform(df[features])

K = 5
km = KMeans(n_clusters=K, n_init=10, random_state=42)
df["cluster"] = km.fit_predict(X)

med = df.groupby("cluster")[features].median()

names = {}
remaining = list(med.index)

inactive = med.loc[remaining, "recency"].idxmax()  
names[inactive] = "inactive"
remaining.remove(inactive)

new = med.loc[remaining, "tenure"].idxmin()       
names[new] = "New customers"
remaining.remove(new)

loyal_order = med.loc[remaining, "monetary"].sort_values().index
for label, c in zip(["Silver", "Gold", "Platinum"], loyal_order):
    names[c] = label

df["group"] = df["cluster"].map(names)

print(df.groupby("group")[features].median().round(1))
print(df["group"].value_counts())

colors = {
    "inactive": "#70c1a5",
    "New customers": "#b4c4d9",
    "Silver": "#c0c0c0",
    "Gold": "#f5c542",
    "Platinum": "#9b7fd1",
}

counts = df["group"].value_counts().sort_values()
fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.barh(counts.index, counts.values, color=[colors[g] for g in counts.index])
for bar, v in zip(bars, counts.values):
    ax.text(v, bar.get_y() + bar.get_height() / 2, f" {v}", va="center")
ax.set_xlabel("number of customers")
plt.tight_layout()
plt.show()

agg = df.groupby("group").agg(
    recency=("recency", "median"),
    frequency=("frequency", "median"),
    spend=("monetary", "mean"),
    n=("user_id", "count"),
)
fig, ax = plt.subplots(figsize=(10, 6))
for g, row in agg.iterrows():
    ax.scatter(row["recency"] / 30, row["frequency"],
               s=row["n"] / agg["n"].max() * 2500 + 100,
               color=colors[g], alpha=0.8)
    ax.annotate(f'Average "{g}": {row["spend"]:.0f}₳',
                (row["recency"] / 30, row["frequency"]),
                textcoords="offset points", xytext=(10, 12))
ax.set_xlabel("Median Recency (month)")
ax.set_ylabel("Median Frequency")
plt.tight_layout()
plt.show()

ix, iy = features.index("frequency"), features.index("monetary")
cluster_colors = ["red", "blue", "green", "cyan", "magenta"]

fig, ax = plt.subplots(figsize=(9, 6))
for c in range(K):
    mask = (df["cluster"] == c).to_numpy()
    ax.scatter(X[mask, ix], X[mask, iy], s=100, color=cluster_colors[c],
               label=f"Cluster {c + 1} ({names[c]})")
ax.scatter(km.cluster_centers_[:, ix], km.cluster_centers_[:, iy],
           s=300, color="yellow", label="Centroids")
ax.set_xlim(-1, 5)      
ax.set_ylim(-2, 5.5)
ax.set_title("Clusters of customers")
ax.set_xlabel("frequency (standardized)")
ax.set_ylabel("monetary value (standardized)")
ax.legend()
plt.tight_layout()
plt.show()