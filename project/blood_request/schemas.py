from pydantic import BaseModel, EmailStr, constr, field_validator
from typing import Optional

class DonorSchema(BaseModel):
    name: constr(min_length=2, max_length=100) # type: ignore
    blood_group: constr(pattern=r'^(A|B|AB|O)[+-]$') # type: ignore
    phone: constr(min_length=10, max_length=15, pattern=r'^\+?1?\d{9,15}$') # type: ignore
    email: Optional[EmailStr] = None
    city: constr(min_length=2, max_length=100) # type: ignore
    state: constr(min_length=2, max_length=100) # type: ignore
    pin_code: constr(min_length=4, max_length=10) # type: ignore
    consent_given: bool
    whatsapp_number: Optional[constr(max_length=15)] = None # type: ignore
    email_notifications: Optional[bool] = False
    available_to_donate: Optional[bool] = True

    @field_validator('phone', 'whatsapp_number', mode='before')
    def clean_phone_fields(cls, v):
        if isinstance(v, str):
            return "".join(c for c in v if c.isdigit() or c == '+')
        return v

    @field_validator('email', mode='before')
    def empty_string_to_none(cls, v):
        if v == "":
            return None
        return v

    @field_validator('consent_given')
    def check_consent(cls, v):
        if not v:
            raise ValueError('Consent must be given to proceed.')
        return v

class BloodRequestSchema(BaseModel):
    city: constr(min_length=2, max_length=100) # type: ignore
    pin_code: constr(min_length=4, max_length=10) # type: ignore
    blood_group: constr(pattern=r'^(A|B|AB|O)[+-]$') # type: ignore
    units: int
    address_line_1: Optional[str] = ""
    address_line_2: constr(min_length=2, max_length=255) # type: ignore
    contact_person: constr(min_length=2, max_length=100) # type: ignore
    contact_phone: constr(min_length=10, max_length=15, pattern=r'^\+?1?\d{9,15}$') # type: ignore
    contact_email: Optional[EmailStr] = None

    @field_validator('contact_phone', mode='before')
    def clean_contact_phone(cls, v):
        if isinstance(v, str):
            return "".join(c for c in v if c.isdigit() or c == '+')
        return v

    @field_validator('contact_email', mode='before')
    def empty_string_to_none(cls, v):
        if v == "":
            return None
        return v
