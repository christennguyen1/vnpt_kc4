from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import sensor_routes
import uvicorn

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sensor_routes.router, tags=['Sensors'], prefix='/api/sensors')

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
