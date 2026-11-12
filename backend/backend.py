from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field, SecretStr

from db.bootstrap_admin import ensure_admin
from db.ReadCommands.auth_read_commands import read_login, read_session_user
from db.ReadCommands.customer_read_commands import (
    read_available_items_in_warehouse,
    read_public_warehouses,
)
from db.sql_commands import connect_and_init
from db.WriteCommands.auth_write_commands import (
    write_change_password,
    write_create_session,
    write_create_user,
    write_delete_session,
    write_signup_customer,
)
from db.WriteCommands.manager_write_commands import (
    write_delete_warehouse,
    write_new_warehouse,
    write_warehouse_privacy,
)
from db.WriteCommands.staff_write_commands import write_delivered_as_InStock
from db.WriteCommands.superior_write_commands import (
    write_motify_markup_price,
    write_order_item,
    write_ordered_as_delivered,
)

# Loads ADMIN_USERNAME / ADMIN_PASSWORD from .env
load_dotenv()

app = FastAPI()

connection = connect_and_init("db/Data/schema.sql", "db/Data/seed.sql")
# Loading the schema drops every account, so the admin is recreated on each start
ensure_admin(connection)

# CORS compatibility. If not here, frontend will block access.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Accounts and sessions
# ---------------------------------------------------------------------------

# Passwords are SecretStr so they never show up in logs or reprs.
class SignupRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    username: str = Field(min_length=3, max_length=100)
    password: SecretStr


class LoginRequest(BaseModel):
    username: str
    password: SecretStr


class ChangePasswordRequest(BaseModel):
    old_password: SecretStr
    new_password: SecretStr


class AdminCreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: SecretStr
    is_admin: bool = False
    customer_id: int | None = None
    employee_id: int | None = None


bearer_scheme = HTTPBearer(auto_error=False)


def get_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    """The session token from the 'Authorization: Bearer <token>' header"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not logged in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


def get_current_user(token: str = Depends(get_token)) -> dict:
    """The logged-in user (user_id, username, role, ...), or 401 if the session is invalid"""
    user = read_session_user(connection, token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    """Only lets the admin through"""
    if not user["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required."
        )
    return user


# Higher roles inherit everything the lower roles can do. Admin is deliberately not ranked:
# it only manages accounts, and has no employee record to attribute changes to.
ROLE_RANK = {
    "Customer": 1,
    "WarehouseStaff": 2,
    "Supervisor": 3,
    "InventoryManager": 4,
}


def require_role(min_role: str):
    """Lets through logged-in users whose role is min_role or higher"""

    def check_role(user: dict = Depends(get_current_user)) -> dict:
        if ROLE_RANK.get(user["role"], 0) < ROLE_RANK[min_role]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your role is not allowed to do this.",
            )
        return user

    return check_role


# POST http://localhost:8000/auth/signup  (customers only)
@app.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(body: SignupRequest):
    user_id = write_signup_customer(
        connection,
        body.name,
        body.email,
        body.phone,
        body.username,
        body.password.get_secret_value(),
    )
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create the account. The username may be taken, the password "
            "may be shorter than 8 characters, or no valid email/phone was given.",
        )
    return {"message": "Account created.", "user_id": user_id}


# POST http://localhost:8000/auth/login
@app.post("/auth/login")
def login(body: LoginRequest):
    user = read_login(connection, body.username, body.password.get_secret_value())
    if user is None:
        # Same message whether the username or the password was wrong
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )
    token = write_create_session(connection, user["user_id"])
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not start a session.",
        )
    return {"token": token, "token_type": "bearer", "user": user}


# POST http://localhost:8000/auth/logout
@app.post("/auth/logout")
def logout(token: str = Depends(get_token), _user: dict = Depends(get_current_user)):
    write_delete_session(connection, token)
    return {"message": "Logged out."}


# GET http://localhost:8000/auth/me
@app.get("/auth/me")
def me(user: dict = Depends(get_current_user)):
    return user


# POST http://localhost:8000/auth/change-password
@app.post("/auth/change-password")
def change_password(
    body: ChangePasswordRequest,
    token: str = Depends(get_token),
    user: dict = Depends(get_current_user),
):
    changed = write_change_password(
        connection,
        user["user_id"],
        body.old_password.get_secret_value(),
        body.new_password.get_secret_value(),
        keep_token=token,
    )
    if not changed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The current password is wrong or the new password is invalid "
            "(8+ characters required).",
        )
    return {"message": "Password changed."}


# POST http://localhost:8000/admin/users  (admin only)
@app.post("/admin/users", status_code=status.HTTP_201_CREATED)
def admin_create_user(
    body: AdminCreateUserRequest, _admin: dict = Depends(require_admin)
):
    user_id = write_create_user(
        connection,
        body.username,
        body.password.get_secret_value(),
        is_admin=body.is_admin,
        customer_id=body.customer_id,
        employee_id=body.employee_id,
    )
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create the user. Check the username is free, the password "
            "is 8+ characters, and the account links to exactly one active customer "
            "or employee (admins link to none).",
        )
    return {"message": "User created.", "user_id": user_id}


# ---------------------------------------------------------------------------
# Inventory (each route needs the minimum role shown; higher roles inherit)
# ---------------------------------------------------------------------------

class NewItemRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    serial_number: str = Field(min_length=1, max_length=50)
    # The defaults are the values this route used before it took a body
    markup_price: float = Field(default=1.00, ge=0)
    category_id: int = 2
    warehouse_id: int = 1


class NewWarehouseRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    # The defaults are the values this route used before it took a body
    street: str = Field(default="1294", max_length=100)
    zip_code: str = Field(default="60623", max_length=10)
    is_public: bool = True


class PriceUpdateRequest(BaseModel):
    new_price: float = Field(ge=0)


class PrivacyUpdateRequest(BaseModel):
    is_public: bool


# http://localhost:8000/  (open: lets anyone check the server is up)
@app.get("/")
def motd():
    item_count = len(read_public_warehouses(connection))
    welcomeMessage = "Database found with " + str(item_count) + " public warehouses"
    print(welcomeMessage)
    return {"Welcome Message": welcomeMessage}


# GET http://localhost:8000/read  (Customer)
@app.get("/read")
def read(_user: dict = Depends(require_role("Customer"))):
    warehouses = read_public_warehouses(connection)
    return {"public warehouses": warehouses}


# GET http://localhost:8000/search?name=Washington%20DC%20Branch  (Customer)
@app.get("/search")
def search(name: str, _user: dict = Depends(require_role("Customer"))):
    items = read_available_items_in_warehouse(connection, name)
    return {"Items": items}


# POST http://localhost:8000/insert  (Supervisor)
@app.post("/insert", status_code=status.HTTP_201_CREATED)
def insert(body: NewItemRequest, user: dict = Depends(require_role("Supervisor"))):
    # The change is recorded against the logged-in employee, never one the client names
    employee_id = user["employee_id"]
    id = write_order_item(
        connection,
        body.warehouse_id,
        body.name,
        body.serial_number,
        body.markup_price,
        body.category_id,
        employee_id,
    )
    if id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not add the item. The serial number may already exist, or the "
            "category or warehouse does not.",
        )

    # Temporary commands to auto-deliver item so it actually shows up with the Search query.
    write_ordered_as_delivered(connection, employee_id, body.serial_number, id)
    write_delivered_as_InStock(connection, employee_id, body.serial_number, id)
    return {"message": f"Added Item ID: {id}", "item_id": id}


# POST http://localhost:8000/insert_warehouse  (InventoryManager)
@app.post("/insert_warehouse", status_code=status.HTTP_201_CREATED)
def insert_warehouse(
    body: NewWarehouseRequest, _user: dict = Depends(require_role("InventoryManager"))
):
    id = write_new_warehouse(
        connection, body.name, body.street, body.zip_code, body.is_public
    )
    if id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not add the warehouse. The name may be taken or the ZIP code "
            "unknown.",
        )
    return {"message": f"Added Warehouse ID: {id}", "warehouse_id": id}


# PUT http://localhost:8000/update/2  with {"new_price": 5.50}  (Supervisor)
@app.put("/update/{id}")
def update(
    id: int,
    body: PriceUpdateRequest,
    _user: dict = Depends(require_role("Supervisor")),
):
    updated_id = write_motify_markup_price(
        connection, body.new_price, item_serial=None, item_id=id
    )
    if updated_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such item, or it is not In Stock.",
        )
    return {"message": f"Item {id} updated successfully."}


# PUT http://localhost:8000/update_warehouse/7  with {"is_public": true}  (InventoryManager)
@app.put("/update_warehouse/{warehouse_id}")
def update_warehouse(
    warehouse_id: int,
    body: PrivacyUpdateRequest,
    _user: dict = Depends(require_role("InventoryManager")),
):
    name = write_warehouse_privacy(connection, warehouse_id, body.is_public)
    if name is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No such warehouse."
        )
    return {"message": f"Warehouse {name} updated successfully."}


# DELETE http://localhost:8000/delete/7  (InventoryManager)
@app.delete("/delete/{id}")
def delete(id: int, _user: dict = Depends(require_role("InventoryManager"))):
    name = write_delete_warehouse(connection, id)
    if name is None:
        # The database refuses to delete a warehouse that still has items or transfers
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No such warehouse, or it is not empty.",
        )
    return {"message": f"Deleted warehouse {name}."}


if __name__ == "__main__":
    import uvicorn

    if connection:
        print("Connected to database")
    else:
        print("Not connected to database")

    uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)
