package com.leafsense.products.repository;

import java.util.List;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.leafsense.products.entity.Product;

@Repository
public interface ProductRepository extends JpaRepository<Product, UUID>{
    List<Product> findByTargetsContainingIgnoreCase(String target);
}
