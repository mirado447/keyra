from fastapi import FastAPI

app = FastAPI()

users = []

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/users")
def post_user(user: str):
    users.append(user)
    return users