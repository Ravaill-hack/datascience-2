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

query = "SELECT user_id, price FROM customers WHERE event_type = 'purchase'"
df = pd.read_sql(query, db)
price = df["price"]

stats = {
    "count": price.count(),
    "mean":  price.mean(),
    "std":   price.std(),
    "min":   price.min(),
    "25%":   price.quantile(0.25),
    "50%":   price.quantile(0.50),
    "75%":   price.quantile(0.75),
    "max":   price.max(),
}

for label, value in stats.items():
    print(f"{label:<8} {value:>14.6f}")

avg_basket_per_user = df.groupby("user_id")["price"].mean()

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
 
axes[0].boxplot(price, vert=False, patch_artist=True)
axes[0].set_title("Prix des articles achetés")
axes[0].set_xlabel("Prix (€)")
axes[0].set_yticks([])
 
axes[1].boxplot(avg_basket_per_user, vert=False, patch_artist=True)
axes[1].set_title("Panier moyen par utilisateur")
axes[1].set_xlabel("Prix moyen du panier (€)")
axes[1].set_yticks([])
 
plt.tight_layout()
plt.savefig("boxplots_price.png")
plt.show()