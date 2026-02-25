const API_BASE = "http://localhost:8080";

async function updatePopupStats() {
  const tokenObj = await chrome.storage.local.get(['sentinel_token']);
  const token = tokenObj.sentinel_token;

  const statusEl = document.getElementById('conn-status');
  const scannedEl = document.getElementById('scanned-count');
  const trustEl = document.getElementById('trust-score');

  try {
    const response = await fetch(`${API_BASE}/api/stats`, {
        headers: {
            'Authorization': `Bearer ${token}` // ✅ Added JWT
        }
    });
    if (!response.ok) throw new Error();

    const data = await response.json();
    
    scannedEl.textContent = data.scanned.toLocaleString();
    trustEl.textContent = `${data.trustScore}%`;
    statusEl.textContent = "Live";
    statusEl.style.background = "#064e3b";
    statusEl.style.color = "#4ade80";
  } catch (err) {
    statusEl.textContent = "Offline";
    statusEl.style.background = "#450a0a";
    statusEl.style.color = "#f87171";
  }
}

// Initial fetch and refresh every 5 seconds while popup is open
updatePopupStats();
setInterval(updatePopupStats, 5000);
