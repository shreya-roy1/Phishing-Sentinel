/**
 * Sentinel Suite: Background Service Worker (Vanilla JS)
 * Handles API calls to bypass Content Script CORS/PNA restrictions.
 */

const API_ENDPOINT = 'http://127.0.0.1:8080/analyze';

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === "PERFORM_SCAN") {
        
        fetch(API_ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(message.data)
        })
        .then(response => {
            if (!response.ok) throw new Error("Network response was not ok");
            return response.json();
        })
        .then(result => {
            sendResponse(result);
        })
        .catch(error => {
            console.error("[Sentinel Background] Fetch Error:", error);
            sendResponse({ error: "API unreachable. Ensure Go server is running on :8080" });
        });

        return true; // Keeps the message channel open for async response
    }
});