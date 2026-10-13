from fastapi import FastAPI, HTTPException

from sql_project.sql_commands import connect_and_init

app = FastAPI()

connection = connect_and_init("Data/schema.sql", "Data/seed.sql")


@app.get("/")
def motd():
    return {"message": "Hello World!"}


@app.get("/search")
def search(name: str):
    raise HTTPException(status_code=501)  # Unimplemented


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

    uvicorn.run("src.sql_project.backend:app", host="127.0.0.1", port=8000, reload=True)
