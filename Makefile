.PHONY: tests

init:
	pip install -r requirements.txt
	cd dependencies/PyMesh; ./setup.py install --user

tests-original:
	python Original/tests/test_sample.py

tests-layered:
	python Layered/tests/test_sample.py
