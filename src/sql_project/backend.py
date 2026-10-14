from fastapi import FastAPI, HTTPException

from sql_project.ReadCommands.customer_read_commands import (
    read_available_items_in_warehouse,
    read_public_warehouses,
)
from sql_project.sql_commands import connect_and_init

app = FastAPI()

connection = connect_and_init("Data/schema.sql", "Data/seed.sql")


# http://localhost:8000/
@app.get("/")
def motd():
    item_count = len(read_public_warehouses(connection))
    welcomeMessage = "Database found with " + str(item_count) + " public warehouses"
    print(welcomeMessage)
    return {"Welcome Message": welcomeMessage}


# http://localhost:8000/read
@app.get("/read")
def read():
    warehouses = read_public_warehouses(connection)
    return {"public warehouses": warehouses}


# http://localhost:8000/search?name=Washington%20DC%20Branch
@app.get("/search")
def search(name: str):
    items = read_available_items_in_warehouse(connection, name)
    return {"Items": items}


@app.post("/insert")
def insert():
    raise HTTPException(status_code=501)  # Unimplemented


@app.post("/update")
def update():
    raise HTTPException(status_code=501)  # Unimplemented


@app.delete("/delete")
def delete():
    raise HTTPException(status_code=501)  # Unimplemented


if __name__ == "__main__":
    import uvicorn

    if connection:
        print("Connected to database")
    else:
        print("Not connected to database")

    uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)
