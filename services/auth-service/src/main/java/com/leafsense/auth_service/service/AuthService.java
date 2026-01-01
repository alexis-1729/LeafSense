package com.leafsense.auth_service.service;

import java.time.LocalDateTime;
import java.util.UUID;
import java.util.logging.Logger;

import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import com.leafsense.auth_service.dto.ChangeEmailRequest;
import com.leafsense.auth_service.dto.ChangePasswordRequest;
import com.leafsense.auth_service.dto.LoginRequest;
import com.leafsense.auth_service.dto.LoginResponse;
import com.leafsense.auth_service.dto.SignUpRequest;
import com.leafsense.auth_service.dto.UserClient.UserRegisteredDTO;
import com.leafsense.auth_service.entity.User;
import com.leafsense.auth_service.repository.UserRepository;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;
    private final UserServiceClient userServiceClient;

    Logger logger = Logger.getLogger(AuthService.class.getName());

    
    /**
     * Register the user if not already registered
     * @param request Email and password (String, String)
     */
    public String signUp(SignUpRequest request){
        if(userRepository.findByEmail(request.email()).isPresent()){
            throw new RuntimeException(request.email() + " has already been registered");
        }

        User user = User.builder()
            .email(request.email())
            .password(passwordEncoder.encode(request.password()))
            .createdAt(LocalDateTime.now())
            .build();

        UserRegisteredDTO newUserClient = new UserRegisteredDTO(
            user.getEmail(),
            user.getCreatedAt()
        );
        
        try{
            userServiceClient.createUser(newUserClient);
            userRepository.save(user);
            return jwtService.generateToken(user); 
        } catch(Exception e){
            logger.info("Error trying to register a user/ trying to set information to User-service");
            logger.info("Exception in com.leafsense.auth_service.service, method singUp");
        }

        return null;
    }

    /**
     * Authenticate a user by verifying their credentials and if valid
     * generate a JWT to allow authorized access to the system
     * @param request Email and password (String, String)
     * @return Jwt 
     */
    public LoginResponse login(LoginRequest request){
        User user = userRepository.findByEmail(request.email())
            .orElseThrow(() -> new RuntimeException("User not found"));

        if(!passwordEncoder.matches(request.password(), user.getPassword())){
            throw new RuntimeException("Invalid password for email: " + request.email());
        }

        LoginResponse response = new LoginResponse(
            jwtService.generateToken(user),
            "Bearer ",
            jwtService.getExpiration()
        );
        return response;
    }

    /**
     * Delete the currently authenticated user and trigger an event
     * notifying other services of the deletion.
     * @param user Authenticated user to be deleted
     */
    public void deleteCurrentUser(String email, UUID id) {
        try{
            logger.info("Attempting to delete user: " + email);;
            //userServiceClient.deleteUser(email);
            userRepository.deleteById(id);
            logger.info("User deleted successfully from both services");
        } catch (Exception e){
            logger.info("Exception in AuthService trying to use method deleteCurrentUser");
        }
    }

    /**
     * Change the password of the authenticated user after verifying
     * the current password is correct.
     * @param user Authenticated user
     * @param request Contains current and new password
     */
    public void changePassword(User user, ChangePasswordRequest request) {

        if (!passwordEncoder.matches(request.currentPassword(), user.getPassword())) {
            throw new RuntimeException("Current password is incorrect");
        }

        user.setPassword(passwordEncoder.encode(request.newPassword()));
        userRepository.save(user);
    }

    /**
     * Change the email of the authenticated user after verifying
     * the current password and ensuring the new email is not already registered.
     * @param user Authenticated user
     * @param request Contains current password and new email
     */
    public void changeEmail(User user, ChangeEmailRequest request){
        
        if(!passwordEncoder.matches(request.currentPassword(), user.getPassword())) {
            throw new RuntimeException("Current password is incorrect");
        }

        if(userRepository.findByEmail(request.newEmail()).isPresent() || request.newEmail().equals(user.getEmail())){
            throw new RuntimeException("Email already registered");
        }

        user.setEmail(request.newEmail());
        userRepository.save(user);
    }
}
