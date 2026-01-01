package com.leafsense.auth_service.dto;

import java.time.LocalDateTime;
import java.util.UUID;

public record MeResponse(
    UUID id,
    String email,
    LocalDateTime createdAt
) {}
