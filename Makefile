.PHONY: help install clear lint dev-env prod-env docker-install
PYTHON_PATH_EXPORT_SERVICE :=  export_service
.DEFAULT: help
help:
	@echo "make install"
	@echo "       creates venv and installs requirements"
	@echo "make dev-env"
	@echo "       run project in dev mode"
	@echo "make prod-env"
	@echo "       run project in production mode"
	@echo "make lint"
	@echo "       run pylint"
	@echo "make clear"
	@echo "       deletes venv and .pyc files"

install:
	python3 -m venv venv
	. venv/bin/activate; \
	pip install setuptools --upgrade; \
	pip install pip --upgrade; \
	pip install -r requirements.txt;

docker-install:
	 pip3 install -r requirements.txt;


clear:
	rm -rf venv
	find -iname "*.pyc" -delete

dev-env:
	 . venv/bin/activate; \
	 export PYTHONPATH=$(PYTHON_PATH_EXPORT_SERVICE); \
	 export FLASK_APP="setup.py"; \
	 export FLASK_ENV="development"; \
	 flask run --port=5000;


prod-env:
	 . venv/bin/activate; \
	 export PYTHONPATH=$(PYTHON_PATH_EXPORT_SERVICE); \
	 export FLASK_APP="setup.py"; \
	 export FLASK_ENV="production"; \
	 flask run --port=5000;

lint:
	. venv/bin/activate; \
	pylint setup.py export_service/