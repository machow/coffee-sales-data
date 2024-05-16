# %%
import polars as pl
import pandas as pd
import polars.selectors as cs
from great_tables import GT
import numpy as np

np.random.seed(111)


# %%
# Generate base data, with revenue and profit ======
simple_table = pl.DataFrame(
    {
        "product": [
            "Grinder",
            "Moka pot",
            "Cold brew",
            "Filter",
            "Drip machine",
            "AeroPress",
            "Pour over",
            "French press",
            "Cezve",
            "Chemex",
            "Scale",
            "Kettle",
            "Espresso Machine",
        ],
        "revenue_dollars": [
            904.50,
            2045.25,
            288.75,
            404.25,
            2632.00,
            2601.50,
            846.00,
            1113.25,
            2512.50,
            3137.25,
            3801.00,
            756.25,
            8406.00,
        ],
        "margin_dollars": [
            567.96,
            181.08,
            241.77,
            70.01,
            1374.45,
            1293.78,
            364.53,
            748.12,
            1969.52,
            817.68,
            2910.29,
            617.52,
            3636.44,
        ],
    }
)

simple_table = simple_table.with_columns(
    cs.ends_with("dollars") * 1000,
    revenue_pct=pl.col("revenue_dollars") / pl.col("revenue_dollars").sum(),
    margin_pct=pl.col("margin_dollars") / pl.col("margin_dollars").sum(),
).select(
    pl.col("product").str.to_lowercase().str.replace(" ", "-").add(".png").alias("icon"),
    pl.col("product"),
    cs.starts_with("revenue"),
    cs.starts_with("margin").name.map(lambda x: x.replace("margin", "profit")),
)

simple_table = (
    pl.concat(
        [
            simple_table,
            simple_table.select(pl.all().sum()).with_columns(product=pl.lit("Total")),
        ]
    )
    .with_columns(cs.ends_with("pct").round(2))
)


# %%
# Note that the code below was hastily generated using chatgpt ----
# Initial data setup
df = simple_table.drop("icon").filter(pl.col("product") != "Total").to_pandas()

# Define typical price points for each type of product
price_points = {
    'Grinder': 120, 'Moka pot': 30, 'Cold brew': 20, 'Filter': 15, 'Drip machine': 100,
    'AeroPress': 30, 'Pour over': 40, 'French press': 25, 'Cezve': 15, 'Chemex': 45,
    'Scale': 150, 'Kettle': 50, 'Espresso Machine': 700
}

# Calculate estimated units sold
df['estimated_units'] = df.apply(lambda x: x['revenue_dollars'] / price_points[x['product']], axis=1)

# Function to generate adjusted monthly sales
def adjusted_monthly_sales(row):
    base_pattern = {
        'Cold brew': [0.2, 0.2, 0.4, 0.8, 1.5, 2, 2, 2, 1.5, 0.8, 0.4, 0.2],
        'Espresso Machine': [0.4, 0.5, 0.4, 0.4, 1.3, .3, .5, .6, .6, .4, .5, 1.5],
        'high_end': [0.7, 0.6, 0.7, 0.8, 0.9, 1.0, 1.0, 0.9, 0.8, 0.8, 0.7, 1.2],
        'medium': [0.8, 0.7, 0.8, 0.9, 1.0, 1.1, 1.1, 1.0, 0.9, 0.9, 0.8, 1.1],
        'low_end': [1.0, 0.9, 1.0, 1.1, 1.2, 1.3, 1.3, 1.2, 1.1, 1.0, 1.0, 1.3]
    }
    # Selecting the pattern based on product type
    pattern = base_pattern['low_end']
    if row["product"] in ["Espresso Machine"]:
        pattern = base_pattern["Espresso Machine"]
    if row['product'] in ['Scale']:
        pattern = base_pattern['high_end']
    elif row['product'] in ['Grinder', 'Kettle', 'Chemex', 'Pour over']:
        pattern = base_pattern['medium']
    elif row['product'] == 'Cold brew':
        pattern = base_pattern['Cold brew']
    
    # Adding random variation to the pattern
    random_variation = np.random.normal(1.0, 0.05, len(pattern))  # 5% standard deviation
    varied_pattern = [p * r for p, r in zip(pattern, random_variation)]

    # Adjusting the pattern to fit the estimated annual unit sales
    annual_sales = row['estimated_units']
    monthly_sales = [round(annual_sales * x / sum(varied_pattern)) for x in varied_pattern]
    return monthly_sales

# Apply the function
df['monthly_sales'] = df.apply(adjusted_monthly_sales, axis=1)

# Adjusting for popularity trends
def apply_popularity_trends(row):
    trend_factor = {
        'Espresso Machine': 1.05,
        'AeroPress': 1.03,
        'Pour over': 1.03,
        'French press': 1.02,
        'Chemex': 1.03,
        'Cold brew': 1.04,
        'Scale': 1.02,
        'Grinder': 1.02,
        'Moka pot': 0.95,
        'Drip machine': 0.95,
        'Filter': 0.99,
        'Kettle': 1.00,  # Stable
        'Cezve': 0.98
    }
    adjusted_sales = []
    for i, sales in enumerate(row['monthly_sales']):
        trend = trend_factor[row['product']] ** (i / 12)
        adjusted_sales.append(round(sales * trend))
    return adjusted_sales

# Apply trend adjustments
df['monthly_sales'] = df.apply(apply_popularity_trends, axis=1)

# %%
# back to human code ----
full_table = simple_table.join(pl.from_pandas(df[["product", "monthly_sales"]]), "product", how="left")
full_table.write_parquet("data/coffee-sales.parquet")
full_table.write_json("data/coffee-sales.json")


# %%
GT(full_table).fmt_nanoplot("monthly_sales", plot_type="bar")
# %%
