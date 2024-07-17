# Install all required dependencies
app-install: 
	pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt


# Start service 
app-start:
	ENV_FILE=.env chainlit run src/main.py


# Test the app
app-test:
	cd src && PYTHONPATH=$(shell pwd)/src pytest --cov=.

