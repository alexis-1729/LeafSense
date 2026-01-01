package com.leafsense.auth_service.controller;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.leafsense.auth_service.dto.ChangeEmailRequest;
import com.leafsense.auth_service.dto.ChangePasswordRequest;
import com.leafsense.auth_service.dto.MeResponse;
import com.leafsense.auth_service.entity.User;
import com.leafsense.auth_service.service.AuthService;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;

import java.util.logging.Logger;

import org.springframework.http.ResponseEntity;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.RequestBody;


@RestController
@RequiredArgsConstructor
@RequestMapping("/api/auth")
@SecurityRequirement(name = "bearerAuth")
public class UserController {

    private final AuthService authService;
    Logger logger = Logger.getLogger(UserController.class.getName());

    /**
     * Retrieves the currently authenticated user's profile.
     * Returns user ID, email, and account creation date.
     *
     * @return ResponseEntity containing user's profile details
     */
    @Operation(
        summary = "Get current authenticated user",
        description = "Returns the user's ID, email, and creation date"
    )
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "User information retrieved"),
        @ApiResponse(responseCode = "401", description = "Unauthorized access")
    })
    @GetMapping("/me")
    public ResponseEntity<MeResponse> getCurrentUser() {
        User user = (User) SecurityContextHolder
        .getContext()
        .getAuthentication()
        .getPrincipal();

        MeResponse response = new MeResponse(
            user.getId(),
            user.getEmail(),
            user.getCreatedAt()
        );

        return ResponseEntity.ok(response);
    }

    /**
     * Deletes the currently authenticated user's account.
     * Triggers a deletion event for downstream services.
     *
     * @return ResponseEntity with no content upon successful deletion
     */
    @Operation(
        summary = "Delete authenticated user",
        description = "Deletes the current user's account and publishes an event"
    )
    @ApiResponses({
        @ApiResponse(responseCode = "204", description = "User deleted successfully"),
        @ApiResponse(responseCode = "401", description = "Unauthorized access")
    })
    @DeleteMapping("/me/delete")
    public ResponseEntity<Void> deleteCurrentUser() {
        User user = (User) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        authService.deleteCurrentUser(user.getEmail(), user.getId());
        return ResponseEntity.noContent().build();
    }

    /**
     * Updates the password of the authenticated user after verifying the current password.
     *
     * @param request Contains current and new password
     * @return ResponseEntity with no content upon successful password change
     */
    @Operation(
        summary = "Change user password",
        description = "Validates current password and updates to new one"
    )
    @ApiResponses({
        @ApiResponse(responseCode = "204", description = "Password updated successfully"),
        @ApiResponse(responseCode = "400", description = "Current password is incorrect"),
        @ApiResponse(responseCode = "401", description = "Unauthorized access")
    })
    @PatchMapping("/me/password")
    public ResponseEntity<Void> changePassword(@Valid @RequestBody ChangePasswordRequest request) {
        User user = (User) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        authService.changePassword(user, request);
        return ResponseEntity.noContent().build();
    }

    /**
     * Updates the email of the authenticated user after verifying the current password.
     *
     * @param request Contains current password and new email
     * @return ResponseEntity with no content upon successful email update
     */
    @Operation(
        summary = "Change user email",
        description = "Validates current password and updates to a new email address"
    )
    @ApiResponses({
        @ApiResponse(responseCode = "204", description = "Email updated successfully"),
        @ApiResponse(responseCode = "400", description = "Email already in use or validation failed"),
        @ApiResponse(responseCode = "401", description = "Unauthorized access")
    })
    @PatchMapping("/me/email")
    public ResponseEntity<Void> changeEmail(@Valid @RequestBody ChangeEmailRequest request) {
        User user = (User) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        authService.changeEmail(user, request);
        return ResponseEntity.noContent().build();
    }
    
}
