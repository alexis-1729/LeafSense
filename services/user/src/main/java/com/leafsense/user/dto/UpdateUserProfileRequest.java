package com.leafsense.user.dto;

import com.leafsense.user.entity.embedded.Location;

public record UpdateUserProfileRequest(
    String email,
    String name,
    String lastName,
    String middleName,
    String phone,
    Location location
) {}
