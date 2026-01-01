package com.leafsense.auth_service.exception;

public class SnsPublishException extends RuntimeException {
    public SnsPublishException(String topicName, Throwable cause){
        super("Failed to publish event to topic: " + topicName, cause);
    }
}
