from pydantic import BaseModel, ConfigDict, Field


class InferRequestV2(BaseModel):
    model_config = ConfigDict(extra="forbid")

    image: str = Field(
        ...,
        description="Image bytes encoded as standard base64, without a data URI prefix",
    )


class ClassScore(BaseModel):
    label: str
    confidence: float = Field(ge=0.0, le=1.0)


class InferResponseV2(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str
    confidence: float = Field(ge=0.0, le=1.0)
    top_k: list[ClassScore]
