
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


def success_response(message: str, data=None, status_code: int = 200):

    return JSONResponse(
        status_code=status_code,
        content={
            "status_code": status_code,
            "success": True,
            "message": message,
            "data": jsonable_encoder(data)
        }
    )


def error_response(message: str, status_code: int = 400, data=None):

    return JSONResponse(
        status_code=status_code,
        content={
            "status_code": status_code,
            "success": False,
            "message": message,
            "data": jsonable_encoder(data)
        }
    )
