package com.leafsense.user.repository;

import java.util.Optional;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.leafsense.user.entity.UserPreferences;

@Repository
public interface UserPreferencesRepository extends JpaRepository<UserPreferences, UUID>{
    Optional<UserPreferences> findByUserProfileId(UUID userProfileId);
    Optional<UserPreferences> findByUserProfile_Email(String email);
}
