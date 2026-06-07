package com.jobscan.service;

import com.jobscan.entity.AnalysisEntity;
import com.jobscan.repository.AnalysisRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.LocalDateTime;

@Service
public class AnalysisService {

    private final AnalysisRepository repository;
    private final RestTemplate restTemplate = new RestTemplate();
    private final ObjectMapper mapper = new ObjectMapper();
    
    @Value("${python.ml.url}")
    private String pythonUrl;

    // Manual Constructor for Dependency Injection
    public AnalysisService(AnalysisRepository repository) {
        this.repository = repository;
    }

    public AnalysisEntity analyze(MultipartFile resume, MultipartFile jd) throws Exception {
        AnalysisEntity entity = new AnalysisEntity();
        entity.setResumeFilename(resume.getOriginalFilename());
        entity.setJdFilename(jd.getOriginalFilename());
        repository.save(entity);
        
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);
        
        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("resume", new ByteArrayResource(resume.getBytes()) {
            public String getFilename() { return resume.getOriginalFilename(); }
        });
        body.add("jd", new ByteArrayResource(jd.getBytes()) {
            public String getFilename() { return jd.getOriginalFilename(); }
        });
        
        ResponseEntity<String> response = restTemplate.exchange(
            pythonUrl + "/analyze",
            HttpMethod.POST,
            new HttpEntity<>(body, headers),
            String.class
        );
        
        JsonNode json = mapper.readTree(response.getBody());
        entity.setMatchScore(json.get("match_score").asDouble());
        entity.setRecommendation(json.get("recommendation").asText());
        entity.setPredictedDomain(json.get("domain").asText());
        entity.setConfidence(json.get("confidence").asDouble());
        entity.setStatus("COMPLETED");
        entity.setCompletedAt(LocalDateTime.now());
        
        return repository.save(entity);
    }
}