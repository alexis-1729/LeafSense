package com.leafsense.auth_service.dto;


public record LoginResponse(
    String accessToken,
    String tokenType, 
    Long expiration 
) {}
