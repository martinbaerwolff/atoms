from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import atoms, persons, projects

app = FastAPI(title="Atoms API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:80"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(persons.router)
app.include_router(projects.router)
app.include_router(atoms.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
