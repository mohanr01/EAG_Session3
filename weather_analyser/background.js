
// Function to check gold rate and send notification if needed
async function checkGoldRate(settings) {
  try {
    const response = await fetch('http://localhost:5000/check_rate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        country: settings.country,
        targetRate: settings.targetRate,
        email: settings.email
      })
    });

    const data = await response.json();
    
    if (data.error) {
      console.error('Error:', data.error);
      return;
    }

    // Update current rate in storage
    chrome.storage.local.set({ currentGoldRate: data.currentRate });
    
    // Notify popup about the update
    chrome.runtime.sendMessage({
      action: 'updateRate',
      rate: data.currentRate
    });

    // Show browser notification if target is reached
    if (data.targetReached) {
      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icons/icon128.png',
        title: 'Temperature Alert!',
        message: `Temperature has reached your target of ${settings.targetRate}! Current Temp: ${data.currentRate}`
      });
    }
  } catch (error) {
    console.error('Error checking Temperature:', error);
  }
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'startMonitoring') {
    const settings = request.settings;
    
    // Clear any existing alarm
    chrome.alarms.clear('checkGoldRate');
    
    // Create new alarm
    chrome.alarms.create('checkGoldRate', {
      periodInMinutes: settings.checkInterval
    });
    
    // Initial check
    checkGoldRate(settings);
  }
});

// Listen for alarm
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'checkGoldRate') {
    chrome.storage.local.get(['settings'], function(result) {
      if (result.settings) {
        checkGoldRate(result.settings);
      }
    });
  }
}); 