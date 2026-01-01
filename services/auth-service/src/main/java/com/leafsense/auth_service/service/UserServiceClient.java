package com.leafsense.auth_service.service;

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import com.leafsense.auth_service.dto.UserClient.UserRegisteredDTO;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class UserServiceClient {

    @Value("${user.service.url}") //value=http://user:8085 /users/
    private String serviceUrl; 
    private final RestTemplate restTemplate;

    public void createUser(UserRegisteredDTO dto){
        restTemplate.postForEntity(serviceUrl + "/users", dto, Void.class);
    }

    public void deleteUser(String email){
        String encodedEmail = URLEncoder.encode(email, StandardCharsets.UTF_8);
        restTemplate.delete(serviceUrl + "/users/" + encodedEmail);
    }
}
