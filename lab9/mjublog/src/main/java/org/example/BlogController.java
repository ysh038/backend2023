package org.example;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RestController;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;

@RestController
public class BlogController {
    @Value("${mju.blog.articles_per_pages}")
    int articlesPerPages;

    @GetMapping("/hello")
    public String hello(){
        return "world!" + articlesPerPages;
    }

    @GetMapping("/config/articles_per_page")
    public int getArticlesPerPage() {
        return articlesPerPages;
    }

    @GetMapping("/article/titles") public Object getArticleTitles() {
        ArrayList<String> a = new ArrayList<>();
        a.add("제목1");
        a.add("제목2");
        return a;
    }

    @GetMapping("/article/{number}")
    public Object getArticle(@PathVariable int number) {
        GetArticleResponse a = new GetArticleResponse();
        a.title = "즐거운 하루";
        a.num = number;
        return a;
    }

    @PostMapping("/article")
    public void postArticle(HttpServletRequest request, HttpServletResponse response) throws IOException{
        System.out.println(request.getMethod());
    }
}
