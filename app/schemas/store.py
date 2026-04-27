from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MerchantOnboardRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Nomad Home",
                "subdomain": "nomad-home",
                "custom_domain": "shop.nomad-home.kz",
                "currency_code": "KZT",
                "timezone": "Asia/Almaty",
            }
        }
    )

    name: str = Field(min_length=2, max_length=120)
    subdomain: str = Field(min_length=3, max_length=80)
    custom_domain: str | None = Field(default=None, max_length=255)
    currency_code: str = Field(default="KZT", min_length=3, max_length=3)
    timezone: str = Field(default="Asia/Almaty", max_length=64)


class StoreRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    subdomain: str
    status: str
    tenant_key: str
    created_at: datetime


class StoreListResponse(BaseModel):
    items: list[StoreRead]
