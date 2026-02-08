// Entry point for Go API

package main

import (
	"bytes"
	"encoding/json"
	"io"
	"log"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

// AnalysisRequest represents the data coming from the extension
type AnalysisRequest struct {
	URL        string                 `json:"url" binding:"required"`
	DOMContent string                 `json:"dom_content" binding:"required"`
	Metadata   map[string]interface{} `json:"metadata"`
}

// AnalysisResponse represents the data returned to the extension
type AnalysisResponse struct {
	IsSpoof         bool     `json:"is_spoof"`
	ConfidenceScore float64  `json:"confidence_score"`
	ThreatLevel     string   `json:"threat_level"`
	Anomalies       []string `json:"detected_anomalies"`
}

func main() {
	r := gin.Default()

	// Middleware for CORS (Allowing the Extension to communicate)
	r.Use(func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}
		c.Next()
	})

	// Health check
	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "API is active", "time": time.Now()})
	})

	// Analysis endpoint - Proxies to the ML Service
	r.POST("/analyze", func(c *gin.Context) {
		var req AnalysisRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		// Forward request to ML Service (FastAPI)
		mlResponse, err := forwardToMLService(req)
		if err != nil {
			log.Printf("ML Service Error: %v", err)
			c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Intelligence layer unreachable"})
			return
		}

		c.JSON(http.StatusOK, mlResponse)
	})

	log.Println("Sentinel API running on :8080")
	r.Run(":8080")
}

func forwardToMLService(data AnalysisRequest) (*AnalysisResponse, error) {
	jsonData, _ := json.Marshal(data)
	
	// Assuming ML service runs on port 8000
	resp, err := http.Post("http://localhost:8000/analyze", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	var result AnalysisResponse
	json.Unmarshal(body, &result)

	return &result, nil
}