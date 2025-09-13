from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from controller.sensors_controller import controller_post_data, controller_get_data_sensor_predict

router = APIRouter()


@router.post("/create")
async def create_sensor_data(request: Request):
    body = await request.json()
    return await controller_post_data(body)

@router.get("/predict")
async def get_data_sensor_predict():
    return await controller_get_data_sensor_predict()
