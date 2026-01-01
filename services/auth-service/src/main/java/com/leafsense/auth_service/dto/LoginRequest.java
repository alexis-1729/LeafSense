package com.leafsense.auth_service.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.Size;

@Schema(description = "Request payload for user login")
public record LoginRequest(
    @Schema(description = "User's email address", example = "user@example.com")
    @Email(message = "Format not valid, it must be an email")
    String email,

    @Schema(description = "User's password, it must contains 6 charcters", example = "securePassword123")
    @Size(min = 6, message = "Password must constains 6 characters")
    String password
) {}
