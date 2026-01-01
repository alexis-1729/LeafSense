package com.leafsense.auth_service.controller;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.leafsense.auth_service.dto.LoginRequest;
import com.leafsense.auth_service.dto.LoginResponse;
import com.leafsense.auth_service.dto.SignUpRequest;
import com.leafsense.auth_service.dto.SignUpResponse;
import com.leafsense.auth_service.service.AuthService;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;


@RestController
@RequiredArgsConstructor
@RequestMapping("/api/auth")
public class AuthController {

    private final AuthService authService;

    /**
     * Handles user registration requests.
     * If successful, returns a JWT token and a confirmation message.
     *
     * @param request Request body containing user's email and password
     * @return ResponseEntity with registration details and JWT token
     */
    @Operation(
        summary = "Register a new user",
        description = "Creates a new user account with email and password and returns a JWT token"
    )
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Authentication successful"),
        @ApiResponse(responseCode = "401", description = "Invalid email or password")
    })
    @PostMapping("/sign-up")
    public ResponseEntity<SignUpResponse> signUp(@Valid @RequestBody SignUpRequest request) {
        String token = authService.signUp(request);
        SignUpResponse response = new SignUpResponse(
            "User registered successfully",
            true,
            request.email(),
            token
        );
        return ResponseEntity.ok(response);
    }

    /**
     * Authenticates a user by verifying credentials.
     * If valid, returns a JWT token for authorized access.
     *
     * @param request Request body containing user's email and password
     * @return ResponseEntity with authentication token and metadata
     */
    @Operation(
        summary = "Authenticate user",
        description = "Validates user credentials and returns a JWT token on success"
    )
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Authentication successful"),
        @ApiResponse(responseCode = "401", description = "Invalid email or password")
    })
    @PostMapping("/login")
    public ResponseEntity<LoginResponse> login(@Valid @RequestBody LoginRequest request) {
        LoginResponse response = authService.login(request);  
        return ResponseEntity.ok(response);
    }
    
}
