# Python application template
The application template aims to provide the basic structure expected by the deployment and build services.

# Basic structure expected by deployment and build services
- main.py: The deployment will invoke this python file when starting the application
- requirements.txt: Requirements will be resolved using content of this file before deployment. Private python package sources are not supported as of now.