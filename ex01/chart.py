import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv("secrets")

postgres_db = os.environ["POSTGRES_DB"]
postgres_user = os.environ["POSTGRES_USER"]
postgres_password = os.environ["POSTGRES_PASSWORD"]

db = create_engine(f"postgresql://{postgres_user}:{postgres_password}@localhost:5432/{postgres_db}")

plt.style.use("seaborn-v0_8-darkgrid")  # fond gris comme sur les exemples

# Récupération des achats uniquement
query = """
SELECT event_time, price, user_id
FROM customers
WHERE event_type = 'purchase'
  AND event_time >= '2022-10-01'
  AND event_time < '2023-03-01'
"""
df = pd.read_sql(query, db)
df["event_time"] = pd.to_datetime(df["event_time"])
df["date"] = df["event_time"].dt.date
df["month"] = df["event_time"].dt.to_period("M")

# ---------- Graphique 1 : nombre de clients par jour (courbe) ----------
customers_per_day = df.groupby("date")["user_id"].nunique()

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(customers_per_day.index, customers_per_day.values)
ax.set_ylabel("Number of customers")
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
plt.show()

# ---------- Graphique 2 : ventes totales par mois (barres, en millions de ₳) ----------
sales_per_month = df.groupby("month")["price"].sum() / 1e6

fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(sales_per_month.index.strftime("%b"), sales_per_month.values, color="lightsteelblue")
ax.set_xlabel("month")
ax.set_ylabel("total sales in million of ₳")
plt.show()

# ---------- Graphique 3 : dépense moyenne par client par jour (aire) ----------
daily = df.groupby("date").agg(total=("price", "sum"), customers=("user_id", "nunique"))
avg_spend = daily["total"] / daily["customers"]

fig, ax = plt.subplots(figsize=(8, 5))
ax.fill_between(avg_spend.index, avg_spend.values, color="lightsteelblue")
ax.set_ylabel("average spend/customers in ₳")
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
plt.show()