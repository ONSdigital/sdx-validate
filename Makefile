build:
	git clone -b 0.7.0 https://github.com/ONSdigital/sdx-common.git
	pip install ./sdx-common
	pip3 install -r requirements.txt
	rm -rf sdx-common

test:
	flake8 --exclude lib
	python3 -m unittest tests/*.py
	pip3 install -r test_requirements.txt

clean:
	rm -rf sdx-common