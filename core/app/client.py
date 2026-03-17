from pydantic import BaseModel, model_validator, field_validator
from typing import Optional


class ScannerClient(BaseModel):
    """A class for managing the credentials of a scanner client"""

    username: Optional[str] = None
    email: Optional[str] = None
    password: str = None
    token: Optional[str] = None
    logged_in: Optional[bool] = False

    @field_validator("username", "email", "token", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        return None if v == "" else v

    @model_validator(mode="after")
    def validate_fields(self):

        not_user_email = not (self.username or self.email)
        if not_user_email:
            raise ValueError("Either username or email must be provided")
        if not self.password:
            raise ValueError("A password must be provided")
        return self
