from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FastRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    started_at: datetime
    ended_at: datetime | None
    duration_seconds: float | None = None


class FastEnd(BaseModel):
    ended_at: datetime | None = None
