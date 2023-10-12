# Thingy Project Orange - Monitoring System for Solar Power Plants
This project is being developped for the "Advanced Software Engineering" course at University of Fribourg, Switzerland. 
## Run the API locally with debug
- Please note that if "python" is not recognized by your machine, try other aliases, like py, python3. Make sure that Python is installed on your system.

- Copy "example.env" to ".env" at the root of the project and adapt if needed. Default values will do for a local environment (localhost:8080).
- Create a virtual environment: ```python -m venv venv``` (or similar, e.g., ```python3 -m venv venv```). 
- Enter the virtual environment: 
  - Mac and Linux: ```source ./venv/bin/activate```
  - Windows: ```.\venv\Scripts\activate.bat``` or ```.\venv\Scripts\Activate.ps1``` for Powershell.
- Inside virtual environment, install all dependencies: ```pip install -r requirements.txt```.
- Once all requirements are installed, run the application using: 
```
python3 run.py
```
- To stop the local server, use ctrl+c
- Finally, read carefully next section to know more about database. Normally, it should be plug and play and no more action is required (unless configurations in .env have been modified)