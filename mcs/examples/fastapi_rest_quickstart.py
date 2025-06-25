# mcs/examples/fastapi_rest_quickstart.py
from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI(
    title="Fibonacci API",
    description="Gibt die n-te Fibonacci-Zahl",
    version="1.0.0",
)


class FibonacciResponse(BaseModel):
    result: int


def fib(n: int) -> int:
    if n < 2:
        return 1
    a, b = 1, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b


# OpenAPI-Spec liegt automatisch unter /openapi.json  (FastAPI-Standard)

@app.get(
    "/tools/fibonacci",
    response_model=FibonacciResponse,
    tags=["Tools"],
    summary="Fibonacci-Zahl",
)
async def get_fibonacci(
    n: int = Query(..., ge=0, description="Position in der Fibonacci-Sequenz"),
):
    """
    Liefert `2 * fib(n)` als JSON.
    """
    return {"result": 2 * fib(n)}


def main() -> None:
    """CLI-Startpunkt: `python -m mcs.examples.fastapi_rest_quickstart`"""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0")


if __name__ == "__main__":
    main()
