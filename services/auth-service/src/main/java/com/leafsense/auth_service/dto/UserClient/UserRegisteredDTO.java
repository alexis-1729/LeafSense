package com.leafsense.auth_service.dto.UserClient;

import java.time.LocalDateTime;

public record UserRegisteredDTO(
    String email,
    LocalDateTime registeredAt
) {}
