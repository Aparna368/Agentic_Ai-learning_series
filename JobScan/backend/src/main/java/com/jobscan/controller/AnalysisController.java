package com.jobscan.controller;

import com.jobscan.dto.AnalysisResponseDTO;
import com.jobscan.entity.AnalysisEntity;
import com.jobscan.service.AnalysisService;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "*")
public class AnalysisController {

    private final AnalysisService service;

    // Manual Constructor for Dependency Injection
    public AnalysisController(AnalysisService service) {
        this.service = service;
    }

    @PostMapping("/analyze")
    public AnalysisResponseDTO analyze(
            @RequestParam("resume") MultipartFile resume,
            @RequestParam("jd") MultipartFile jd) throws Exception {
        
        AnalysisEntity result = service.analyze(resume, jd);
        
        AnalysisResponseDTO dto = new AnalysisResponseDTO();
        dto.setAnalysisId(result.getId());
        dto.setMatchScore(result.getMatchScore());
        dto.setRecommendation(result.getRecommendation());
        dto.setDomain(result.getPredictedDomain());
        dto.setConfidence(result.getConfidence());
        dto.setStatus(result.getStatus());
        return dto;
    }
}