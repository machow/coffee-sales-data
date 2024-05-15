all: coffee-sales.json coffee-sales.parquet README.md coffee-table.png

coffee-sales.json coffee-sales.parquet: 1-generate.py
	python 1-generate.py

README.md coffee-table.png: README.qmd
	quarto render README.qmd