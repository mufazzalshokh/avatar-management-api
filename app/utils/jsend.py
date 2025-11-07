from typing import Any, Optional
from fastapi.responses import JSONResponse


class JSendResponse:
    """
    JSend response formatter according to JSend specification
    https://github.com/omniti-labs/jsend
    """

    @staticmethod
    def success(data: Any = None, status_code: int = 200) -> JSONResponse:
        """
        Success response when everything went well

        Args:
            data: The data to return
            status_code: HTTP status code (default: 200)
        """
        return JSONResponse(
            status_code=status_code,
            content={
                "status": "success",
                "data": data
            }
        )

    @staticmethod
    def fail(data: Any, status_code: int = 400) -> JSONResponse:
        """
        Fail response when the request failed due to client error

        Args:
            data: Error details or validation errors
            status_code: HTTP status code (default: 400)
        """
        return JSONResponse(
            status_code=status_code,
            content={
                "status": "fail",
                "data": data
            }
        )

    @staticmethod
    def error(message: str, code: Optional[int] = None, data: Any = None, status_code: int = 500) -> JSONResponse:
        """
        Error response when the request failed due to server error

        Args:
            message: Error message
            code: Application-specific error code
            data: Additional error data
            status_code: HTTP status code (default: 500)
        """
        response_data = {
            "status": "error",
            "message": message
        }

        if code is not None:
            response_data["code"] = code

        if data is not None:
            response_data["data"] = data

        return JSONResponse(
            status_code=status_code,
            content=response_data
        )