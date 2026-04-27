from pydantic import BaseModel, EmailStr


class AddressInput(BaseModel):
    country: str
    city: str
    address_line1: str
    postal_code: str


class OrderItemInput(BaseModel):
    variant_id: str
    quantity: int


class OrderCreate(BaseModel):
    customer_email: EmailStr
    items: list[OrderItemInput]
    shipping_address: AddressInput
