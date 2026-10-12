import os

import matplotlib.pyplot as plt
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv("secrets")

db = create_engine(
    f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}"
    f"@localhost:5432/{os.environ['POSTGRES_DB']}"
)

plt.style.use("seaborn-v0_8-darkgrid")

# Une ligne par client : nombre de commandes et total dépensé
query = """
SELECT user_id,
       COUNT(*)   AS frequency,
       SUM(price) AS monetary
FROM customers
WHERE event_type = 'purchase'
  AND event_time >= '2022-10-01'
  AND event_time <  '2023-03-01'
GROUP BY user_id
"""
df = pd.read_sql(query, db)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Histogramme 1 : nombre de clients selon la fréquence d'achat
# (l'affichage est limité au 99.5e percentile pour la lisibilité,
#  les données ne sont pas supprimées)
fmax = df["frequency"].quantile(0.995)
axes[0].hist(df["frequency"], bins=5, range=(df["frequency"].min(), fmax),
             color="lightsteelblue", edgecolor="white")
axes[0].set_xlabel("frequency")
axes[0].set_ylabel("customers")

# Histogramme 2 : nombre de clients selon le montant dépensé (en ₳)
mmax = df["monetary"].quantile(0.995)
axes[1].hist(df["monetary"], bins=5, range=(df["monetary"].min(), mmax),
             color="lightsteelblue", edgecolor="white")
axes[1].set_xlabel("monetary value in ₳")
axes[1].set_ylabel("customers")

plt.tight_layout()
plt.show()
