.PHONY: tests

init:
	pip install -r requirements.txt
	cd dependencies/PyMesh; ./setup.py install --user

tests:
	python tests/test_sample.py