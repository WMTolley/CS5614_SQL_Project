# Database Frontend

This frontend provides an interface for accessing the database. 

To use:

1. Ensure node.js is installed.
2. `./run_frontend.sh` to launch the interface through Vite.
3. Access the interface through [http://localhost:5173/](http://localhost:5173/).

### Database not connecting?

Ensure your DevContainer is running, and the backend is enabled and on port 8000:

`python src/sql_project/backend.py`

### Bash script not running?

`chmod 777 run_frontend.sh`

### Bash script crashing due to carriage return?

`sed -i 's/\r$//' run_frontend.sh`