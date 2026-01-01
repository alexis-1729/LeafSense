package com.leafsense.user.dto;

import java.time.LocalDateTime;

public record CreateUserRequest(
    String email,
    LocalDateTime registeredAt
) {

}
