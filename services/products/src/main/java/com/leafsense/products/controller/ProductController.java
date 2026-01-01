package com.leafsense.products.controller;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.leafsense.products.dto.ProductDTO;
import com.leafsense.products.service.ProductService;

import lombok.RequiredArgsConstructor;

import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

@RestController
@RequestMapping("/api/product")
@RequiredArgsConstructor
public class ProductController {

    private final ProductService productService;

    @GetMapping("/by-target/{target}")
    public ResponseEntity<List<ProductDTO>> getByTarget(@PathVariable String target) {
        return ResponseEntity.ok(productService.getByTargets(target));
    }
    
}
