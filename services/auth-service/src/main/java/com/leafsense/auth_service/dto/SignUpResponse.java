package com.leafsense.auth_service.dto;

public record SignUpResponse(
    String data,
    boolean success,
    String email,
    String token
) {}
