from services.sensors_services import  service_post_all_data
from fastapi.responses import JSONResponse


async def controller_post_data(body):
    try:
        data, status = await service_post_all_data(body)
        response = {
            "message": data.get('message'),
            "data": data.get('data'),
            "status": status,
            "errCode": 0
        }
        return JSONResponse(content=response, status_code=status)
    except Exception as e:
        return {
            "status": 500,
            "message": str(e),
            "error": 1
        }, 500

