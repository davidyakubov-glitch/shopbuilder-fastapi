from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AttributeAxisInput(BaseModel):
    name: str = Field(examples=["Size"])
    values: list[str] = Field(examples=[["S", "M", "L"]], min_length=1)


class InventoryLocationInput(BaseModel):
    name: str = Field(examples=["Almaty Warehouse"])
    city: str | None = Field(default=None, examples=["Almaty"])
    default_quantity_per_variant: int = Field(default=0, ge=0, examples=[10])


class ProductVariantMatrixRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Minimal Hoodie",
                "handle": "minimal-hoodie",
                "vendor": "Nomad Essentials",
                "base_sku": "NH-HOODIE",
                "price_amount": 18990,
                "attributes": [
                    {"name": "Size", "values": ["S", "M"]},
                    {"name": "Color", "values": ["Black", "White"]},
                    {"name": "Material", "values": ["Cotton"]},
                ],
                "locations": [
                    {"name": "Almaty Warehouse", "city": "Almaty", "default_quantity_per_variant": 10}
                ],
            }
        }
    )

    title: str
    handle: str
    vendor: str | None = None
    description_html: str | None = None
    base_sku: str
    price_amount: int = Field(gt=0)
    attributes: list[AttributeAxisInput] = Field(min_length=1)
    locations: list[InventoryLocationInput] = Field(min_length=1)


class VariantInventoryRead(BaseModel):
    location_name: str
    available_qty: int


class VariantRead(BaseModel):
    sku: str
    title: str
    price_amount: int
    inventory: list[VariantInventoryRead]


class VariantMatrixResponse(BaseModel):
    product_id: str
    generated_variant_count: int
    variants: list[VariantRead]


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    handle: str
    status: str
    created_at: datetime


class CursorPage(BaseModel):
    next_cursor: str | None
    has_more: bool


class ProductListResponse(BaseModel):
    items: list[ProductRead]
    page: CursorPage
