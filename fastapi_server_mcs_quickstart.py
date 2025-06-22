from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.openapi.utils import get_openapi
import json
from pydantic import BaseModel

app = FastAPI(
    title="Fibonacci API",
    description="Berechnet die n-te Fibonacci-Zahl.",
    version="1.0.0"
)


class FibonacciResponse(BaseModel):
    result: str


def fibonacci(n: int) -> int:
    if n <= 1:
        return max(0, n)
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


@app.get("/openapi-html", response_class=HTMLResponse)
async def openapi_as_html():
    spec = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes
    )
    spec_json = json.dumps(spec, indent=2, ensure_ascii=False)
    html = f"""
    <html>
        <head><title>OpenAPI Spezifikation</title></head>
        <body>
            <h1>OpenAPI Spezifikation</h1>
            <pre>{spec_json}</pre>
        </body>
    </html>
    """
    return HTMLResponse(content=html)


# HTML-Endpunkt für Browser
@app.get("/tools/fibonacci", response_class=HTMLResponse, tags=["Tools"])
async def get_fibonacci_html(
    n: int = Query(..., description="Die Position in der Fibonacci-Sequenz. Nur positive ganze Zahlen erlaubt.")
):
    result = fibonacci(n)
    result = 2 * result
    html = f"<html><body><h1>Ergebnis: {result}</h1></body></html>"
    return HTMLResponse(content=html, status_code=200)
