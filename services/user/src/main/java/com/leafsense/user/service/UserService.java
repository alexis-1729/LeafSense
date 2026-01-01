package com.leafsense.user.service;

import java.util.UUID;

import org.springframework.stereotype.Service;

import com.leafsense.user.dto.CreateUserRequest;
import com.leafsense.user.dto.UpdateUserPreferencesRequest;
import com.leafsense.user.dto.UpdateUserProfileRequest;
import com.leafsense.user.dto.UserPreferencesDTO;
import com.leafsense.user.dto.UserProfileDTO;
import com.leafsense.user.entity.UserPreferences;
import com.leafsense.user.entity.UserProfile;
import com.leafsense.user.repository.UserPreferencesRepository;
import com.leafsense.user.repository.UserProfileRepository;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class UserService {

    private final UserProfileRepository userProfileRepository;
    private final UserPreferencesRepository userPreferencesRepository;

    public void createUser(CreateUserRequest request) {
        UserProfile user = UserProfile.builder()
            .email(request.email())
            .registeredAt(request.registeredAt())
            .build();

        userProfileRepository.save(user);
        
    }

    public void updateUserPreferences(UUID userId, UpdateUserPreferencesRequest request) {
        UserPreferences preferences = userPreferencesRepository.findByUserProfileId(userId)
            .orElseThrow(() -> new RuntimeException("Preferences not found"));

        preferences.setNotificationsEnable(request.notificationsEnable());
        userPreferencesRepository.save(preferences);
    }


    public UserProfileDTO convertToDTO(UserProfile profile){
        return new UserProfileDTO(
            profile.getId(),
            profile.getName(),
            profile.getLastName(),
            profile.getMiddleName(),
            profile.getEmail(),
            profile.getPhone(),
            profile.getLocation(),
            profile.isActive()
        );
    }

    public void updateUserProfile(UUID id, UpdateUserProfileRequest request) {
        UserProfile profile = userProfileRepository.findById(id)
            .orElseThrow(() -> new RuntimeException("User not found"));

        profile.setName(request.name());
        profile.setEmail(request.email());
        profile.setLastName(request.lastName());
        profile.setMiddleName(request.middleName());
        profile.setPhone(request.phone());
        profile.setLocation(request.location());

        userProfileRepository.save(profile);
    }

    public UserPreferencesDTO convertToDTO(UserPreferences preferences) {
        return new UserPreferencesDTO(preferences.isNotificationsEnable());
    }

    public UserProfile getUserById(UUID id) {
        return userProfileRepository.findById(id).orElse(null);
    }

    public void deleteUser(String email){
        userProfileRepository.deleteByEmail(email);
    }

    public UserPreferences getPreferencesByUserId(UUID userId) {
        return userPreferencesRepository.findByUserProfileId(userId).orElse(null);
    }

    //drop this
    public void createUser(UserProfile user){
        userProfileRepository.save(user);
    }
}
