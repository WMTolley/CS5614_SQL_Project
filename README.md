# CS5614 SQL Python Dev Container Info :


## To Start Project:

1. If you don't already have Visual Studio Code (VSCode), download it to your computer. (https://code.visualstudio.com/)
1. If you don't already have DockerDesktop, download it to your computer. (https://docs.docker.com/desktop/)
1. Open DockerDesktop
1. Open VSCode and click "File" -> "Open Folder" and select the folder you want as your project's parent.
1. Run: `git clone https://github.com/WMTolley/CS5614_SQL_Project.git`
1. Click "File" -> "Open Folder" and select the created folder.
1. If using windows immedietely run `git stash` after cloning to reverse WindowOS's changes.
1. Press: `Ctrl + Shift + P`
1. Click Dev Containers: Reopen in Container
1. This should have created your Dev Container succesfully.


## To Reopen Container (Once you've already started the project):

1. Open DockerDesktop
1. Open VSCode and click "File" -> "Open Folder" and select this project's folder.
1. Press: `Ctrl + Shift + P`
1. Clicked Dev Containers: Reopen in Container  
1. This should have opened your Dev Container succesfully.


## To Rebuild Container (Rebuilds Cache):

1. Open DockerDesktop
1. Open VSCode and click "File" -> "Open Folder" and select this project's folder.
1. Press: `Ctrl + Shift + P`
1. Clicked Dev Containers: Rebuild Container Without Cache  
1. This should have fully rebuilt your Dev Container succesfully.


## Walk Through:

### For a basic view:
Run `tree --charset=ascii`  
Or Run `tree -a --charset=ascii`  
Or Run `tree -a -f --charset=ascii`  
### For each file:
- **.devcontainer/**: &emsp;Handles the Dev container  
- **data/**: &emsp;To store any *.sql, *.csv, *.json, or other database files  
- **src/**: &emsp;Contains the code of the actual project.  
- **tests/**: &emsp;Contains the tests of the project, separated since the client doesn't need them when the project is deployed.   
- **.gitignore**: &emsp;The files that shouldn't be shared when uploaded with git.  
- **init_project.sh**: &emsp;Bash file that can be run with the command `./init_project.sh` to easily initialize the database.
- **Makefile**: &emsp;Automates frequent processes, using the `make` command-line tool.  
- **pyproject.toml**: &emsp;Configuration file for this python project. Included to support the mutmut tool.  
- **README.md**: &emsp;What you are reading right now.  
- **requirements.txt**: &emsp;The libraries the user will need to install (Done automatically in devcontainer).  
- **run_project.sh**: &emsp;Bash file that can be run with the command `./run_pylint.sh` to easily run the project.  
- **run_pylint.sh**: &emsp;Bash file that can be run with the command `./run_pylint.sh` to easily run pylint.  
- **run_pytest.sh**: &emsp;Bash file that can be run with the command `./run_pytest.sh` to easily run pytest.  


## Troubleshooting:

1. **If you get the error: failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine; check if the path is correct and if the daemon is running: open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.**  
Just opening the Docker Desktop application fixes this error.
  
1.  **In case you want to remove all python libraries to determine whats necessary I would recommend the command:**   
`pip freeze | xargs pip uninstall -y`  

1. If you wish to add/remove python libraries from requirements.txt to only include whats necessary, I recommend the command:
`pipdeptree --warn silence | grep -E '^\w+' > requirements.txt`

1. In case you want to remove all python libraries, I would recommend the command:
`pip freeze | xargs pip uninstall -y`

1. If you ever need to redownload the python librarires manually:
While in the root/code directory
Run `pip install -r requirements.txt`

## Notes:

### To Create a New Basic Container:
1. Create .devcontainer directory  
1. Create devcontainer.json file (can use code we used)  
1. Create Dockerfile.dev file (can use code we used)  
1. Open DockerDesktop  
1. Press ctrl+shift+p  
1. Click Dev Containers: Reopen in Container  
1. This should have created your Dev Container succesfully.

### To Initialize Database:
1. While in the root/code directory  
1. Run either `make init` or `python -m src.sql_project.init`  

### To Run Project:
1. First Initialize Database
1. While in the root/code directory  
1. Run either `make run` or `python -m src.sql_project.continue`  

### To Test Project:
1. While in the root/code directory  
1. You can run the command `./run_pytest.sh` or to do it manually:  
    1. If there is a directory named ./mutants delete it and all its contents  
    1. Run `python -m pytest`  
1. For code coverage run: `python -m pytest --cov=src --cov-report=term-missing --cov-branch`  
1. For an html report:  
    1. Run `python -m pytest --cov=src --cov-report=html --cov-branch`  
    1. Run `python -m http.server 8080 --directory htmlcov`  
    1. In a browser go to: http://localhost:8080/  

### To Statically Analyze Code:
1. While in the root/code directory  
1. You can run the command `./run_pylint.sh` or to do it manually:  
    1. If there is a directory named ./mutants delete it and all its contents  
    1. Run `pylint src`  
    1. If you wish to instead analyze the test files code run `pylint tests`  
    1. To instead output in the form of a JSON object to a file run:  
        `pylint --output-format=json . > pylint.coverage`  
1. This should list the detected flaws for each file, also listing the line number of the problem, which should be formatted similar to this (if there are any):  
    &emsp;&emsp;************* Module main  
    &emsp;&emsp;src/project/main.py:14:7: C0303: Trailing whitespace (trailing-whitespace)  
    &emsp;&emsp;src/project/main.py:17:0: C0116: Missing function or method docstring  
    &emsp;&emsp;(missing-function-docstring)  
    &emsp;&emsp;************* Module pets.dog  
    &emsp;&emsp;src/project/pets/dog.py:21:4: C0116: Missing function or method docstring  
    &emsp;&emsp;(missing-function-docstring)  
1. At the bottom seperated by a horizontal line should be a rating of your code, for example:  
    &emsp;&emsp;"Your code has been rated at 9.30/10 (previous run: 9.30/10, +0.00)"  

### To Mutate Test:
1. While in the root/code directory  
1. Run `make mutate` or `mutmut run`  
1. The terminal should show a count of 7 icons:  
    1. The party icon is how many mutants were created and caught.  
    1. The straight face icon is how many mutants were created and explicitly skipped.  
    1. The clock icon is how many mutants were created and timed out.  
    1. The suspicious face icon is how many mutants were created on an already failing test.  
    1. The frowning face icon is how many mutants were created and never caught.  
    1. The muted icon is how many mutants with an invalid syntax were created.  
    1. The wizard icon is for more complex results.  
1.  To view the results run `mutmut results`, which should output a result like formated similar to this (if not all mutants were caught):  
    &emsp;&emsp;project.main.x_firstPrime__mutmut_3: survived  
    &emsp;&emsp;project.main.x_firstPrime__mutmut_5: survived  
    &emsp;&emsp;project.main.x_firstPrime__mutmut_6: survived  
    &emsp;&emsp;project.main.x_firstPrime__mutmut_8: survived  
    &emsp;&emsp;project.main.x_firstPrime__mutmut_12: survived  
1. To examine the changes a specific mutant contained run `mutmut show <mutant id>`. For example: `mutmut show sql_project.sql_commands.x_remove_student_safely__mutmut_8`  

### When Delivering:
* **Libraries**:  
    Since this is a python project, run `pip freeze > requirements.txt`  
    This will create a file named requirements.txt listing all the libraries installed, like Flask, pandas, or requests.  
    The client will need this file and to run `pip install -r requirements.txt` (this is done already with the dev container, but can also be done manually) to install all the libraries you have.  
    If you get the warning that starts with "WARNING": Running pip as the 'root' user" and you want to use a virtual environment then. Run the following three commands for a virtual environment:   
            &emsp;&emsp;python -m venv venv (Creates the isolated environment)  
            &emsp;&emsp;source venv/bin/activate (Activates it—on Windows use venv\Scripts\activate)  
            &emsp;&emsp;pip install -r requirements.txt (Installs everything safely)   
* **Dockerfile.dev**:
    WHen delivering a different Dockerfile will be necessary, one that doesn't include the now unnecessary development tools.

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
