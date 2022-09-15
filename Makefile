init:
	pip install -r requirements.txt

test:
	python -m pytest

coverage:
	python -m coverage run -m pytest
	coverage xml
	coverage html

run:
	uvicorn main:app --reload

demo:
	python main_demo.py

.PHONY: init test