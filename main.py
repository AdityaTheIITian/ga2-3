import time
import uuid

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

EMAIL = "23f1003148@ds.study.iitm.ac.in"
ALLOWED_ORIGIN = "https://dash-cbqrbz.example.com"

app = FastAPI()

# Added first, so it sits inside the header middleware below.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],  # exact origin only, no wildcard
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
)


# Added last, so it is the outermost layer and stamps EVERY response,
# including preflights and CORS rejections.
@app.middleware("http")
async def add_headers(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = str(uuid.uuid4())
    response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.6f}"
    return response


@app.get("/stats")
async def stats(values: str = Query(...)):
    try:
        nums = [int(v) for v in values.split(",") if v.strip() != ""]
    except ValueError:
        raise HTTPException(status_code=400, detail="values must be comma-separated integers")
    if not nums:
        raise HTTPException(status_code=400, detail="no values provided")
    total = sum(nums)
    return {
        "email": EMAIL,
        "count": len(nums),
        "sum": total,
        "min": min(nums),
        "max": max(nums),
        "mean": total / len(nums),
    }