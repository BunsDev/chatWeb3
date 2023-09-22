# Path: api/api_endpoints.py
from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from api.routers.well_known import get_ai_plugin, get_host, well_known
from api.services.blockchain_data import (
    BlockchainDataError,
    query_blockchain_data_from_flipside,
)

ai_plugin = get_ai_plugin()

app = FastAPI(
    title=ai_plugin["name_for_human"],
    description=ai_plugin["description_for_human"],
    version="0.1.0",
)

# origins = [
#     "https://chat.openai.com",
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat.openai.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(well_known)


class ChatWeb3QueryRequest(BaseModel):
    query: str = Field(
        ...,
        description="A natural English language query to query blockchain data",
    )


@app.post("/query_blockchain_data", include_in_schema=True)
async def query_chatweb3(data: ChatWeb3QueryRequest, request: Request):
    """Query blockchain data using a natural English language query
    and get the answer as well as the thought process
    """
    try:
        answer, thought_process = query_blockchain_data_from_flipside(data.query)
        return {"answer": answer, "thought_process": thought_process}
    except BlockchainDataError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"error": "Internal server error" + str(e)}
        )


@app.exception_handler(BlockchainDataError)
async def unicorn_exception_handler(request: Request, exc: BlockchainDataError):
    return JSONResponse(
        status_code=400,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )


def start():
    import uvicorn

    uvicorn.run("api.api_endpoints:app", host="localhost", port=8000, reload=True)