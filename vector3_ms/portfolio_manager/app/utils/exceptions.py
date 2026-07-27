from fastapi import HTTPException

def not_found(message="Resource not found"):
    raise HTTPException(status_code=404, detail=message)

def bad_request(message="Bad request"):
    raise HTTPException(status_code=400, detail=message)

class UnauthorizedException(Exception):
    def __init__(self, message="Unauthorized"):
        self.message = message
        raise HTTPException(status_code=401, detail=message)

class UserAlreadyExistsException(Exception):
    def __init__(self, message="User already exists"):
        self.message = message
        raise HTTPException(status_code=409, detail=message)
