from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sql_project.ReadCommands.customer_read_commands import (
    read_available_items_in_warehouse,
    read_public_warehouses,
)
from sql_project.sql_commands import connect_and_init
from sql_project.WriteCommands.manager_write_commands import (
    write_delete_warehouse,
    write_new_warehouse,
    write_warehouse_privacy,
)
from sql_project.WriteCommands.superior_write_commands import (
    write_motify_markup_price,
    write_order_item,
)

app = FastAPI()

connection = connect_and_init("Data/schema.sql", "Data/seed.sql")

# CORS compatibility. If not here, frontend will block access.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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


# http://localhost:8000/insert/hello/sjfe
@app.get("/insert/{name}/{serial_number}")
def insert(name: str, serial_number: str):
    id = write_order_item(connection, 1, name, serial_number, 1.00, 2, 1)
    return {"Added Item_ID:": id}


# http://localhost:8000/insert_warehouse/great
@app.get("/insert_warehouse/{name}")
def insert_warehouse(name: str):
    id = write_new_warehouse(connection, name, "1294", "60623", True)
    return {"Added Warehouse_ID:": id}


# http://localhost:8000/update/2/5.50
@app.get("/update/{id}/{new_price}")
def update(id: int, new_price: float):
    write_motify_markup_price(connection, new_price, item_serial=None, item_id=id)
    return {"message": f"Item {id} updated successfully"}


# http://localhost:8000/update_warehouse/7/true
@app.get("/update_warehouse/{warehouse_id}/{is_public}")
def update_warehouse(warehouse_id: int, is_public: bool):
    name = write_warehouse_privacy(connection, warehouse_id, is_public)
    return {"message": f"Warehouse {name} updated successfully"}


# http://localhost:8000/delete/7
@app.get("/delete/{id}")
def delete(id: int):
    name = write_delete_warehouse(connection, id)
    return {"You deleted": name}


if __name__ == "__main__":
    import uvicorn

    if connection:
        print("Connected to database")
    else:
        print("Not connected to database")

    uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)
