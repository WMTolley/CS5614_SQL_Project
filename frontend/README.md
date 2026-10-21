# Database Frontend

This frontend provides an interface for accessing the database. 

To use:

1. Ensure node.js is installed.
2. `npm install` to install dependencies.
3. `./frontend.sh` to launch the interface through Vite.
4. Access the interface through [http://localhost:5173/](http://localhost:5173/).

### Database not connecting?

Ensure your DevContainer is running, and the backend is enabled and on port 8000:

`python src/sql_project/backend.py`

### Bash script not running?

`chmod 777 frontend.sh`