from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["API UI"])

@router.get("/scalar", response_class=HTMLResponse)
def scalar_ui():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Scalar API Console</title>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@scalar/themes@latest/style.css" />
        <style>
            body {
                margin: 0;
                padding: 0;
            }
        </style>
    </head>
    <body>
        <script id="api-reference" data-url="/openapi.json" src="https://cdn.jsdelivr.net/npm/@scalar/api-reference@latest"></script>
    </body>
    </html>
    """
