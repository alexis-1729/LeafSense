package com.leafsense.products.service;

import java.util.List;
import java.util.Objects;
import java.util.stream.Stream;

import org.springframework.stereotype.Service;

import com.leafsense.products.dto.ProductDTO;
import com.leafsense.products.entity.Product;
import com.leafsense.products.enums.ProductType;
import com.leafsense.products.repository.ProductRepository;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class ProductService {

    private final ProductRepository productRepository;

    public List<ProductDTO> getByTargets(String target){
        List<Product> allProducts = productRepository.findByTargetsContainingIgnoreCase(target);

        Product agronomic = allProducts.stream()
            .filter(p -> p.getType() == ProductType.AGRONOMIC)
            .findFirst().orElse(null);

        Product biochemical = allProducts.stream()
            .filter(p -> p.getType() == ProductType.BIOCHEMICAL)
            .findFirst().orElse(null);

        return Stream.of(agronomic, biochemical)
            .filter(Objects::nonNull)
            .map(this::toDTO)
            .toList();
    }

    public ProductDTO toDTO(Product product){
        return new ProductDTO(
            product.getName(),
            product.getBrand(),
            product.getDescription(),
            product.getIngredients(),
            product.getFormulationType(),
            product.getType(),
            product.getImageUrl()
        );
    }
}
