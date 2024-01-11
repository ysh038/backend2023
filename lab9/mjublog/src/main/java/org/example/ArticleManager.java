package org.example;

import jakarta.annotation.PostConstruct;
import lombok.Getter;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class ArticleManager {
    @Autowired
    ArticleRepository articleRepository;

    public List<String> getTitles(){
        List<String> ret = new ArrayList<>();
        for (Article article : articleRepository.findAll()){
            ret.add(article.getTitle());
        }
        return ret;
    }

    public String getTitleAt(int index){
        Article article = articleRepository.findById((long) index).orElseThrow();
        return  article.getTitle();
    }

    public void append(String title){
        Article article = Article.builder()
                .title(title)
                .build();
        articleRepository.save(article);
    }
}
