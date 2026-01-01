package com.leafsense.auth_service.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.Size;

public record SignUpRequest(
    @Email(message = "Format not valid, it must to be email")
    String email,

    @Size(min = 6, message = "Password must contains 6 characters")
    String password
) {}
