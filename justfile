install:
  uv sync

lint: 
  ruff check . 

format:
  ruff format .

fix: 
  ruff check --fix .

test: 
  pytest

clean: 
  ruff clean 
  rm -rf __pycache__ .pytest_cache
