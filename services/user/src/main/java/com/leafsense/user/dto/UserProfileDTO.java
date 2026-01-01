package com.leafsense.user.dto;

import java.util.UUID;

import com.leafsense.user.entity.embedded.Location;

public record UserProfileDTO(
    UUID id,
    String name, 
    String lastName, 
    String middleName,
    String email, 
    String phone, 
    Location location,
    boolean isActive
) {} 
