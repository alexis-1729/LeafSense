
package com.leafsense.products.initializer;

import java.util.List;
import java.util.Set;

import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import com.leafsense.products.entity.Product;
import com.leafsense.products.enums.ProductType;
import com.leafsense.products.repository.ProductRepository;

import lombok.RequiredArgsConstructor;

@Component
@RequiredArgsConstructor
public class ProductDataLoader implements CommandLineRunner {

    private final ProductRepository productRepository;

    @Override
    public void run(String... args){
        if(productRepository.count() == 0){
            productRepository.saveAll(List.of(
                Product.builder()
                    .name("Captan 50 WP")
                    .brand("ADAMA México")
                    .description("Captan 50% WP Fungicida agrícola a base de captan en polvo humectable para el control de Antracnosis, Cenicilla, Mancha foliar, Mancha Negra, Mancha púrpura, Mildiú, Moho gris, Peca de la hoja, Roña, Tizón foliar, Tizón temprano y Tizón tardío en cultivos de Berenjena, Calabacita, Cebolla, Chile, Fresa, Jitomate, Mango, Manzano, Melón, Pepino, Sandía, Ornamentales, Peral, Vid y Zanahoria")
                    .ingredients(List.of("Captan 50%"))
                    .formulationType("Polvo humectable")
                    .type(ProductType.BIOCHEMICAL)
                    .targets(Set.of("Apple___Black_rot"))
                    .imageUrl("http://products-service:8084/images/Apple___Black_rot_B.png")
                    .build(),

                Product.builder()
                    .name("ROOTSHIELD PLUS")
                    .brand("BioWorks")
                    .description("Es un fungicida biológico preventivo para el control de enfermedades de las plantas. Ayuda a que las raíces crezcan más rápido y más fuertes, permitiendo que sus cultivos toleren una amplia gama de enfermedades y de condiciones adversas, mientras mejora la salud general de las plantas, resultando en cultivos de alta calidad")
                    .ingredients(List.of("Microbios", "Esporas de Trichoderma harzianum Rifai", "Cepa T-22", "Trichoderma virens cepa G-41"))
                    .formulationType("Polvo mojable")
                    .type(ProductType.AGRONOMIC)
                    .targets(Set.of("Apple___Black_rot", "Apple___Apple_scab"))
                    .imageUrl("http://products-service:8084/images/Apple___Black_rot_A.png")
                    .build(),
                
                // AGROQUÍMICO para Sarna del Manzano
                Product.builder()
                    .name("SYLLIT 400 SC")
                    .brand("Lanafil")
                    .description("Fungicida de amplio espectro con acción preventiva y erradicante. Controla sarna del manzano y del peral (Venturia sp.) en ambas caras de la hoja.")
                    .ingredients(List.of("Dodine 400 g/L SC"))
                    .formulationType("Suspensión Concentrada")
                    .type(ProductType.BIOCHEMICAL)
                    .targets(Set.of("Apple___Apple_scab"))
                    .imageUrl("http://products-service:8084/images/Apple___Apple_scab_B.png")
                    .build(),

                // AGROQUÍMICO para Roya común del maíz
                Product.builder()
                    .name("Crelyon")
                    .brand("BASF")
                    .description("Fungicida con efecto fisiológico que mejora rendimiento y calidad. Control prolongado de enfermedades hasta por 14 días.")
                    .ingredients(List.of("Mefentrifluconazol", "Piraclostrobina"))
                    .formulationType("Suspensión concentrada")
                    .type(ProductType.BIOCHEMICAL)
                    .targets(Set.of("Corn_(maize)_Cercospora_leaf_spot Gray_leaf_spot"))
                    .imageUrl("http://products-service:8084/images/Corn_(maize)_Cercospora_leaf_spot Gray_leaf_spot_B.png")
                    .build(),

                // AGROQUÍMICO para Tizón temprano de la patata
                Product.builder()
                    .name("Legasus")
                    .brand("BASF")
                    .description("Fungicida de fácil dilución con acción sistémica. Mejora la administración de energía y la calidad de cosechas.")
                    .ingredients(List.of("Pyraclostrobin", "Metiram"))
                    .formulationType("Gránulos Dispersables")
                    .type(ProductType.BIOCHEMICAL)
                    .targets(Set.of("Pepper,bell__healthy"))
                    .imageUrl("http://products-service:8084/images/Pepper,bell__healthy_B.png")
                    .build(),

                // AGROECOLÓGICO para Roya común del maíz
                Product.builder()
                    .name("Serenade® ASO")
                    .brand("Bayer CropScience México")
                    .description("Biofungicida para enfermedades foliares. Promueve defensas naturales y compatible con agricultura orgánica.")
                    .ingredients(List.of("Bacillus subtilis cepa QST 713"))
                    .formulationType("Suspensión concentrada")
                    .type(ProductType.AGRONOMIC)
                    .targets(Set.of("Corn_(maize)_Cercospora_leaf_spot Gray_leaf_spot"))
                    .imageUrl("http://products-service:8084/images/Corn_(maize)_Cercospora_leaf_spot Gray_leaf_spot_A.png")
                    .build(),

                // AGROECOLÓGICO para Tizón temprano de la patata
                Product.builder()
                    .name("BioNeem Plus")
                    .brand("EcoVital Bioproductos S.A. de C.V.")
                    .description("Fungicida vegetal para control de tizón temprano. Refuerza inmunidad vegetal y repele insectos vectores.")
                    .ingredients(List.of("Extracto de semilla de Neem", "Aceite esencial de tomillo", "Extracto de canela", "Saponinas naturales de yucca"))
                    .formulationType("Concentrado emulsionable (CE)")
                    .type(ProductType.AGRONOMIC)
                    .targets(Set.of("Pepper,bell__healthy"))
                    .imageUrl("http://products-service:8084/images/Pepper,bell__healthy_A.png")
                    .build()

            ));
        }
    }

}
