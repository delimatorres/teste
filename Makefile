.PHONY: help tests run

help:
	@echo
	@echo "Please use 'make <target>' where <target> is one of"
	@echo "  install        to install dependencies"
	@echo "  test_install   to install test dependencies"
	@echo "  test        to run tests"
	@echo "  clean       to clean compiled files"
	@echo "  run         to run the script"
	@echo
install:
	@pip install -r requirements/default.txt

test_install:
	@pip install -r requirements/test.txt

test: tests_install clean
	@python -m unittest discover

clean:
	@find . -name "*.pyc" -delete

run:
	@python foodbasket