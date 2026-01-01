package com.leafsense.products.entity;

import java.util.List;
import java.util.Set;
import java.util.UUID;

import com.leafsense.products.enums.ProductType;

import jakarta.persistence.CollectionTable;
import jakarta.persistence.Column;
import jakarta.persistence.ElementCollection;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.Lob;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class Product {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    private String name;
    private String brand;
    private String imageUrl;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String description;
    private String formulationType;

    @ElementCollection
    private List<String> ingredients;

    @Enumerated(EnumType.STRING)
    private ProductType type;

    @ElementCollection
    @CollectionTable(name = "product_targets", joinColumns = @JoinColumn(name = "product_id"))
    private Set<String> targets;

}
