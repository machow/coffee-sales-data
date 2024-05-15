# Coffee sales data


``` python
import polars as pl
import polars.selectors as cs
from great_tables import GT, loc, style

coffee_sales = pl.read_json("coffee-sales.json")
```

``` python
sel_rev = cs.starts_with("revenue")
sel_prof = cs.starts_with("profit")


coffee_table = (
    GT(coffee_sales)
    .tab_header("Sales of Coffee Equipment")
    .tab_spanner(label="Revenue", columns=sel_rev)
    .tab_spanner(label="Profit", columns=sel_prof)
    .cols_label(
        revenue_dollars="Amount",
        profit_dollars="Amount",
        revenue_pct="Percent",
        profit_pct="Percent",
        monthly_sales="Monthly Sales",
        icon="",
        product="Product",
    )
    # formatting ----
    .fmt_number(
        columns=cs.ends_with("dollars"),
        compact=True,
        pattern="${x}",
        n_sigfig=3,
    )
    .fmt_percent(columns=cs.ends_with("pct"), decimals=0)
    # style ----
    .tab_style(
        style=style.fill(color="aliceblue"),
        locations=loc.body(columns=sel_rev),
    )
    .tab_style(
        style=style.fill(color="papayawhip"),
        locations=loc.body(columns=sel_prof),
    )
    .tab_style(
        style=style.text(weight="bold"),
        locations=loc.body(rows=pl.col("product") == "Total"),
    )
    .fmt_nanoplot("monthly_sales", plot_type="bar")
    .fmt_image("icon", path="assets")
    .sub_missing(missing_text="")
)

coffee_table.save("coffee-table.png",  scale=2)
```

![An image of a Great Table output, which is an HTML table. Each row is
a coffee product](./coffee-table.png)
