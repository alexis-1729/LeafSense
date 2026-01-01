package com.leafsense.auth_service.dto.UserClient;

import jakarta.validation.constraints.Email;

public record UserDeleteDTO(
    @Email(message = "It must be an email")
    String email    
) {

}
