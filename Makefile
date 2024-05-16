all: data/coffee-sales.json data/coffee-sales.parquet data/coffee-table.png README.md 

data/coffee-sales.json data/coffee-sales.parquet: scripts/1-generate.py
	python $<

README.md data/coffee-table.png: README.qmd data/coffee-sales.json
	quarto render $<