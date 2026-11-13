# CS5614 Inventory Management System

A multi-warehouse inventory system built on PostgreSQL, with a Python (FastAPI) backend and a React frontend. Customers browse public warehouses and their available items, and employees manage items and warehouses according to their role. Every login has one of five roles, and the backend enforces what each role is allowed to do.


## Features

- **Role-based access.** Four inventory roles form a hierarchy in which each higher role inherits everything below it. A fifth role, Admin, only manages accounts.

  | Role | Can do |
  |---|---|
  | Customer | View public warehouses and the available items in them (read only) |
  | Warehouse Staff | Everything a Customer can |
  | Supervisor | Everything Staff can, plus create items and change an item's markup price |
  | Inventory Manager | Everything a Supervisor can, plus create warehouses, change a warehouse's public/private setting, and delete empty warehouses |
  | Admin | Create customer, employee, and admin logins. Admin has no employee record, so it cannot do any inventory action |

- **Accounts and sessions.** Customers can sign up themselves. Admins create logins for existing customers and employees. Users can log in, log out, and change their own password. Passwords are stored as bcrypt hashes, and sessions store only a hash of the token and last 24 hours.
- **Audit trail.** Adding an item records each status change (Ordered, Delivered, In Stock) against the logged-in employee. The employee comes from the session and never from the request.
- **Public and private warehouses.** Customers only see warehouses marked public.
- **Database-enforced rules.** Examples are non-negative prices, six allowed item statuses, different origin and destination warehouses on a transfer, and `RESTRICT` on deleting a warehouse that still has items.
- **Sample data and report.** `db/Data/seed.sql` holds synthetic data for every table, and `db/sample_report.py` prints sample rows, queries, and constraint demonstrations for the project report.

### Current limitations

- New items are marked delivered and in stock immediately. This is temporary code in the `/insert` route.
- Warehouse Staff has no actions of its own yet. The staff and reserve status changes exist as database commands but have no API routes.
- Price and warehouse changes are not recorded in an audit table.
- The backend reloads `schema.sql` and `seed.sql` every time it starts, which resets all data and accounts.


## Setup

### Requirements

1. [Visual Studio Code](https://code.visualstudio.com/) with the Dev Containers extension
1. [Docker Desktop](https://docs.docker.com/desktop/)

### First-time setup

1. Open Docker Desktop.
1. Clone the project: `git clone https://github.com/WMTolley/CS5614_SQL_Project.git`
1. In VS Code, click "File" -> "Open Folder" and select the cloned folder.
1. On Windows, run `git stash` right after cloning to reverse Windows' line-ending changes.
1. Press `Ctrl + Shift + P` and click **Dev Containers: Reopen in Container**.

This builds two containers: one for Python and Node.js, and a PostgreSQL 16 container named `db`. The Python libraries from `requirements.txt` are installed automatically. Port 5173 is forwarded for the frontend.

### Create the admin login

The backend creates the admin account from environment variables, so no password is stored in the code. In the project root, create a file named `.env` (it is ignored by git):

```
ADMIN_USERNAME=admin
ADMIN_PASSWORD=choose-a-password-of-8-or-more-characters
```

### Run the project

Use two terminals inside the dev container, both from the project root:

1. **Backend:** `./run_backend.sh` starts the API at http://127.0.0.1:8000. On start it loads `db/Data/schema.sql` and `db/Data/seed.sql` and creates the admin account.
1. **Frontend:** `./run_frontend.sh` installs the npm packages and starts the app. Open http://localhost:5173 in a browser.

To log in as someone other than the admin, sign up as a customer on the login screen, or log in as the admin and create employee logins for the seeded employees (for example employee ID 1 is a Supervisor and 4 is an Inventory Manager). Interactive API documentation is available at http://127.0.0.1:8000/docs.

### Reset the database without starting the backend

Run `./run_init.sh`. It reloads the schema and seed data and runs a set of example queries.

### Reopen or rebuild the container

- **Reopen:** open Docker Desktop, open the project folder in VS Code, press `Ctrl + Shift + P`, and click **Dev Containers: Reopen in Container**.
- **Rebuild:** do the same but click **Dev Containers: Rebuild Container Without Cache**.


## Sample Report Output

With the database loaded, run:

```
python -m db.sample_report            # uses the data already in the database
python -m db.sample_report --init     # reloads schema.sql and seed.sql first
python -m db.sample_report > report.txt
```

It prints the first five rows of every table, 12 sample queries with results, and 8 statements that break a rule and are rejected by the database. It adds demo accounts and sessions so those tables have rows, then rolls everything back, so your data is not changed.


## Testing and Code Quality

### Tests

Run `./run_pytest.sh`, or `python -m pytest` directly. The tests need the database to be reachable. To run them against a different Postgres, set `TEST_DB_HOST` and `TEST_DB_PORT`.

For code coverage:

1. Run `python -m pytest --cov=db --cov=backend --cov-report=term-missing --cov-branch`
1. For an HTML report, use `--cov-report=html` instead, then run `python -m http.server 8080 --directory htmlcov` and open http://localhost:8080/

### Static analysis

Run `./run_pylint.sh` (it runs `pylint .`). It lists each flaw with its file, line number, and a rating out of 10 at the bottom. To write the results as JSON, run `pylint --output-format=json . > pylint.coverage`.

### Frontend lint

From the `frontend` folder, run `npm run lint`.


## Project Structure

- **backend/**: &emsp;The FastAPI application (`backend.py`) with the account, session, and inventory routes.
- **db/**: &emsp;All database code.
  - **Data/**: `schema.sql` (tables and constraints), `seed.sql` (synthetic sample data), and `inventory_testing.sql` (data used by tests).
  - **ReadCommands/** and **WriteCommands/**: The SQL commands, grouped by the role that uses them (customer, staff, superior, manager, auth).
  - `auth.py`: Password hashing and session token helpers.
  - `bootstrap_admin.py`: Creates the admin account from `.env`.
  - `sql_commands.py`: The database connection settings and helpers.
  - `inventory_init.py`: Reloads the database and runs example queries.
  - `sample_report.py`: Prints the report output described above.
- **frontend/**: &emsp;The React app, built with Vite.
- **Tests/**: &emsp;The pytest tests for authentication, role permissions, the data, and the read commands.
- **.devcontainer/**: &emsp;The Dev Container setup (Python container plus the PostgreSQL 16 `db` container).
- **Makefile**: &emsp;Shortcuts for `make lint`, `make test`, `make backend`, and `make frontend`. Run `make` to see the list.
- **pyproject.toml**: &emsp;Configuration for pylint.
- **requirements.txt**: &emsp;The Python libraries (installed automatically in the dev container).
- **run_backend.sh**, **run_frontend.sh**, **run_init.sh**, **run_pytest.sh**, **run_pylint.sh**: &emsp;Scripts that run each part of the project.


## Troubleshooting

1. **Error: failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine ...**  
Open the Docker Desktop application. This fixes the error.

1. **"Database container not reachable".**  
The code connects to the host `db`, which only exists inside the dev container. Make sure you reopened the project in the container, and that Docker Desktop is running.

1. **The admin cannot log in or `WARNING: ADMIN_USERNAME / ADMIN_PASSWORD not set` appears.**  
Create the `.env` file described above and restart the backend. The password must be at least 8 characters.

1. **Everything is gone after restarting the backend.**  
This is expected. The backend reloads the schema and seed data on every start.

1. **To reinstall the Python libraries manually**, run `pip install -r requirements.txt` from the project root.


## Sources / Additional Resources:

"Psycopg - PostgreSQL adapter for Python"  
by Psycopg  
https://www.psycopg.org/#home  
https://www.psycopg.org/  

"Use Postgres with Python"  
by Brandon Rohrer  
https://www.brandonrohrer.com/postgres_intro.html  
https://www.brandonrohrer.com/blog.html  

"PostgreSQL Python - Querying Data"  
by GeeksForGeeks  
https://www.geeksforgeeks.org/python/postgresql-python-querying-data/  
https://www.geeksforgeeks.org/  

"Development or Dev Containers in 5 minutes"  
by COMMAND  
https://www.youtube.com/watch?v=Un2Nw00oL2s  
https://www.youtube.com/@cmd_labs  

"Docker Desktop"  
by DockerDocs  
https://docs.docker.com/desktop/  
https://www.docker.com/products/docker-desktop/  

"Developing in Python with Dev Containers — Part 1: Setup"  
by Andy Pickup  
https://andypickup.com/developing-in-python-with-dev-containers-part-1-setup-f1aeb89cbfed  
https://andypickup.com/  

"Setting A Dockerized Python Environment — The Elegant Way"  
by Rami Krispin  
https://medium.com/data-science/setting-a-dockerized-python-environment-the-elegant-way-f716ef85571d  
https://medium.com/@rami.krispin  

"Create a Dev Container"  
by Visual Studio Code  
https://code.visualstudio.com/docs/devcontainers/create-dev-container  
https://code.visualstudio.com/  
