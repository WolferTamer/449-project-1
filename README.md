# 449-project-1
A Flask project that uses CRUD operations to manage a hypothetical inventory system

## Initialize Project
1. Clone the repository and ensure python & pip are installed
2. Create a new python environment. The exact method varies by machine, but in general you can use `python -m venv venv`
3. Run the python environment with `.\venv\Scripts\activate`  
4. Run `pip install -e .`
6. Run `flask --app project_1 run`
## Start Project
Run `flask run`
## Additional Notes
- When adding new requirements to the project, make sure to run `pip freeze > requirements.txt` in the base folder so that everyone else can get them too.
- On Windows you may have restrictions on running scripts such as virtual environments, to get around this you can run `Set-ExecutionPolicy Unrestricted`.