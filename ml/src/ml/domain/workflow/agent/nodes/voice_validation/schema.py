from pydantic import BaseModel


class VoiceValidationResponse(BaseModel):
    voice_is_valid: bool
