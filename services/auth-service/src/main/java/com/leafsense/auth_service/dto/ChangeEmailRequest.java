package com.leafsense.auth_service.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.Size;

public record ChangeEmailRequest(
    @Email(message = "Format invalid, it must be an email")
    String newEmail,

    @Size(min = 6, message = "Password must contains 6 characters")
    String currentPassword
) {}
