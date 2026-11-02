from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routes.auth import router as auth_router
from routes.recommend import router as recommend_router
from routes.filter import router as filter_router
from routes.compare import router as compare_router
from routes.dashboard import router as dashboard_router
from database import get_connection, init_db_schema

app = FastAPI(title="SmartDine API")


@app.on_event("startup")
def startup_event():
    init_db_schema()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(recommend_router)
app.include_router(filter_router)
app.include_router(compare_router)
app.include_router(dashboard_router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Unexpected server error"})

@app.get("/")
def root():
    return {"message": "SmartDine API running"}

@app.get("/health")
def health_check():
    try:
        conn = get_connection()
        conn.close()
        return {"status": "ok", "database": "connected"}
    except Exception:
        return JSONResponse(status_code=503, content={"status": "error", "database": "unreachable"})