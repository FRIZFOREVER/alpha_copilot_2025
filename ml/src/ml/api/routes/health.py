from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/ping")
async def ping():
    return {"message": "pong"}


@router.get("/ollama")
async def ollama():
    # TODO: check init state

    # TODO: check awailable and running models

    raise NotImplementedError()


@router.get("/health")
async def health():
    # TODO: check init state

    raise NotImplementedError()
