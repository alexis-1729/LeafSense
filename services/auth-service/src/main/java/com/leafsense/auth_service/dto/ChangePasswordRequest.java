package com.leafsense.auth_service.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Size;

@Schema(description = "Payload for changing the user's password")
public record ChangePasswordRequest(
    @Schema(description = "Current password, it must contains 6 characters", example = "oldPassword123")
    @Size(min = 6, message = "Password must be contain at least 6 character")
    String currentPassword,

    @Schema(description = "New password, it must contains 6 characters", example = "newPassword123")
    @Size(min = 6, message = "Password must be contain at least 6 character")
    String newPassword
) {}
