init:
	pip3 install -r requirements.txt

test:
	python3 -m pytest

coverage:
	python3 -m coverage run -m pytest
	coverage xml

.PHONY: init test