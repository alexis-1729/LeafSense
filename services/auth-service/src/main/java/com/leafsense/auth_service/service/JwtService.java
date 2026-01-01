package com.leafsense.auth_service.service;

import java.nio.charset.StandardCharsets;
import java.util.Date;

import javax.crypto.SecretKey;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import com.leafsense.auth_service.entity.User;

import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;

@Service
public class JwtService {

    @Value("${jwt.secret-key}")
    private String secretKey;

    @Value("${jwt.expiration}")
    private Long expiration;
    
    /**
     * this method transforms secretKey in a valid type
     * to signWith
     * @return 
     */
    private SecretKey getSigningKey() {
        byte[] keyBytes = secretKey.getBytes(StandardCharsets.UTF_8); 
        return Keys.hmacShaKeyFor(keyBytes);
    }

    /**
     * Generate a signed JWT for a specific user, including it's basic
     * data and configuring it's expiration time
     * @param user
     * @return
     */
    public String generateToken(User user){
        return Jwts.builder()
            .subject(user.getId().toString())
            .claim("email", user.getEmail())
            .issuedAt(new Date())
            .expiration(new Date(System.currentTimeMillis() + expiration))
            .signWith(getSigningKey(), Jwts.SIG.HS256)
            .compact();
    }

    /**
     * Verify if a JWT is valid for a specific user, fulfilling two conditions:
     * -User ID in the token matches the user ID provided
     * -The token has not expired
     * @param token
     * @param user 
     * @return 
     */
    public boolean isTokenValid(String token, User user){
        String userId = extractUserId(token);
        return userId.equals(user.getId().toString()) && !isTokenExpired(token);
    }

    /**
     * Extract the user ID from a JWT without validating it's expiration
     * @param token 
     * @return 
     */
    public String extractUserId(String token){
        return Jwts.parser()
            .verifyWith(getSigningKey())
            .build()
            .parseSignedClaims(token)
            .getPayload()
            .getSubject();
    }

    /**
     * Determine if a JWT token has expired by comparing it's expiration date
     * with the current date
     * @param token 
     * @return 
     */
    public boolean isTokenExpired(String token){
        Date expiration = Jwts.parser()
            .verifyWith(getSigningKey())               
            .build()
            .parseSignedClaims(token)      
            .getPayload()                  
            .getExpiration();

        return expiration.before(new Date());
    }

    /**
     * 
     * @return token expiration
     */
    public Long getExpiration(){
        return expiration;
    }

}
