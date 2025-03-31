document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('monitorForm');
  const monitoringStatus = document.getElementById('monitoringStatus');
  const currentRate = document.getElementById('currentRate');

  // Load saved settings
  chrome.storage.local.get(['isMonitoring', 'settings', 'currentGoldRate'], function(result) {
    if (result.isMonitoring) {
      monitoringStatus.textContent = 'Monitoring';
      if (result.currentGoldRate) {
        currentRate.textContent = `${result.currentGoldRate}`;
      }
      
      // Populate form with saved settings
      if (result.settings) {
        document.getElementById('country').value = result.settings.country;
        document.getElementById('targetRate').value = result.settings.targetRate;
        document.getElementById('email').value = result.settings.email;
        document.getElementById('checkInterval').value = result.settings.checkInterval;
      }
    }
  });

  form.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const settings = {
      country: document.getElementById('country').value,
      targetRate: parseFloat(document.getElementById('targetRate').value),
      email: document.getElementById('email').value,
      checkInterval: parseInt(document.getElementById('checkInterval').value)
    };

    // Save settings and start monitoring
    chrome.storage.local.set({
      settings: settings,
      isMonitoring: true
    }, function() {
      monitoringStatus.textContent = 'Monitoring';
      
      // Send message to background script to start monitoring
      chrome.runtime.sendMessage({
        action: 'startMonitoring',
        settings: settings
      });
    });
  });

  // Listen for updates from background script
  chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action === 'updateRate') {
      currentRate.textContent = `${request.rate}`;
    }
  });
}); 