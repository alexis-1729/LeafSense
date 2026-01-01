package com.leafsense.user.repository;

import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.leafsense.user.entity.UserProfile;

@Repository
public interface UserProfileRepository extends JpaRepository<UserProfile, UUID>{
    void deleteByEmail(String email);
}
