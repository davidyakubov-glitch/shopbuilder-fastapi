from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"example": {"email": "owner@example.com", "password": "StrongPass!2026"}}
    )

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if not any(character.isupper() for character in value):
            raise ValueError("Password must include at least one uppercase letter.")
        if not any(character.islower() for character in value):
            raise ValueError("Password must include at least one lowercase letter.")
        if not any(character.isdigit() for character in value):
            raise ValueError("Password must include at least one digit.")
        if not any(not character.isalnum() for character in value):
            raise ValueError("Password must include at least one special character.")
        return value


class LoginRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"example": {"email": "owner@example.com", "password": "StrongPass!2026"}}
    )

    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"refresh_token": "c29tZS1yZWZyZXNoLXRva2Vu"}})

    refresh_token: str


class LogoutRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"refresh_token": "c29tZS1yZWZyZXNoLXRva2Vu"}})

    refresh_token: str


class EmailVerificationRequest(BaseModel):
    token: str = Field(min_length=20)


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=20)
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        return RegisterRequest.validate_password_strength(value)


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class LogoutResponse(BaseModel):
    message: str = "Refresh token revoked."


class MessageResponse(BaseModel):
    message: str
