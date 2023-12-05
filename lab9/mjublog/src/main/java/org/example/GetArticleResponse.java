package org.example;

import com.fasterxml.jackson.annotation.JsonProperty;

public class GetArticleResponse{
    @JsonProperty("제목")
    String title;
    @JsonProperty("글번호")
    int num;
}