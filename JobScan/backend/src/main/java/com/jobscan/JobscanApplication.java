package com.jobscan;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class JobscanApplication {
    public static void main(String[] args) {
        SpringApplication.run(JobscanApplication.class, args);
        System.out.println("🚀 JobScan Backend Started on port 5000!");
    }
}