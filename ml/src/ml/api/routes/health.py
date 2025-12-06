from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok"}


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
    return {"status": "ok"}
