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
        <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
    </head>
    <body style="margin:0;padding:0;">
        <api-reference 
            data-url="/openapi.json"
            theme="dark"
            layout="modern"
            hide-sidebar="false"
            hide-schema="false"
            hide-header="false">
        </api-reference>
    </body>
    </html>
    """
