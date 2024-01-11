package org.example;

import jakarta.persistence.*;
import lombok.*;

@Entity(name = "article")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Article {
    @Id
    @GeneratedValue (strategy = GenerationType.IDENTITY)
    @Column(name = "id", updatable = false)
    private Long number;

    @Column(name = "title",nullable = false)
    private String title;
}
