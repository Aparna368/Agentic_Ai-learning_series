package com.jobscan.repository;

import com.jobscan.entity.AnalysisEntity;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AnalysisRepository extends JpaRepository<AnalysisEntity, Long> {
}