package com.leafsense.products.dto;

import java.util.List;

import com.leafsense.products.enums.ProductType;

public record ProductDTO(
    String name,
    String brand,
    String description,
    List<String> ingredients,
    String formulation,
    ProductType type,
    String imageUrl
) {

}
