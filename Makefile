build:
	pip install -r requirements.txt

test: build
	python3 -m unittest tests/*.py