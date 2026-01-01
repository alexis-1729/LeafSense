package com.leafsense.auth_service.exception;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import com.leafsense.auth_service.dto.ErrorResponse;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(SnsPublishException.class)
    public ResponseEntity<ErrorResponse> handleSnsError(SnsPublishException ex) {
        return ResponseEntity.status(HttpStatus.BAD_GATEWAY)
            .body(ErrorResponse.of("SNS_PUBLISH_ERROR", ex.getMessage()));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGeneric(Exception ex) {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(ErrorResponse.of("GENERIC_ERROR", "Unexpected error occurred."));
    }

}
