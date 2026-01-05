/**
 * Google Apps Script to Keep Render Backend Awake
 * 
 * This script pings your Render backend every 10 minutes to prevent it from sleeping.
 * 
 * SETUP INSTRUCTIONS:
 * 1. Go to https://script.google.com
 * 2. Create a new project
 * 3. Paste this code
 * 4. Update BACKEND_URL with your actual Render backend URL
 * 5. Click "Run" > "pingBackend" to test
 * 6. Click "Triggers" (clock icon) > "Add Trigger"
 * 7. Configure:
 *    - Function: pingBackend
 *    - Event source: Time-driven
 *    - Type: Minutes timer
 *    - Interval: Every 10 minutes
 * 8. Save and authorize the script
 */

// ⚙️ CONFIGURATION - Update this with your actual backend URL
const BACKEND_URL = 'https://hug-pdf-backend.onrender.com/api/';

/**
 * Main function to ping the backend
 * This will be triggered every 10 minutes
 */
function pingBackend() {
  try {
    const startTime = new Date();
    
    // Make HTTP GET request to backend health check endpoint
    const response = UrlFetchApp.fetch(BACKEND_URL, {
      method: 'GET',
      muteHttpExceptions: true, // Don't throw errors on non-200 responses
      followRedirects: true,
      validateHttpsCertificates: true
    });
    
    const endTime = new Date();
    const responseTime = endTime - startTime;
    const statusCode = response.getResponseCode();
    const responseText = response.getContentText();
    
    // Log the result
    if (statusCode === 200) {
      Logger.log(`✅ SUCCESS: Backend is awake (${responseTime}ms) - ${statusCode}`);
      Logger.log(`Response: ${responseText.substring(0, 100)}`);
    } else {
      Logger.log(`⚠️ WARNING: Unexpected status code ${statusCode} (${responseTime}ms)`);
      Logger.log(`Response: ${responseText.substring(0, 100)}`);
    }
    
    // Optional: Send email alert if backend is down (uncomment if needed)
    // if (statusCode !== 200) {
    //   sendAlertEmail(statusCode, responseText);
    // }
    
  } catch (error) {
    Logger.log(`❌ ERROR: Failed to ping backend - ${error.message}`);
    
    // Optional: Send email alert on error (uncomment if needed)
    // sendAlertEmail('ERROR', error.message);
  }
}

/**
 * Optional: Send email alert when backend is down
 * Uncomment the function calls above to enable
 */
function sendAlertEmail(statusCode, message) {
  const email = Session.getActiveUser().getEmail();
  const subject = `🚨 HugPDF Backend Alert - Status: ${statusCode}`;
  const body = `
    Backend Health Check Failed
    
    Time: ${new Date().toLocaleString()}
    Status: ${statusCode}
    URL: ${BACKEND_URL}
    
    Details:
    ${message}
    
    Please check your Render dashboard: https://dashboard.render.com
  `;
  
  MailApp.sendEmail(email, subject, body);
}

/**
 * Test function to verify the script works
 * Run this manually to test before setting up the trigger
 */
function testPing() {
  Logger.log('🧪 Testing backend ping...');
  pingBackend();
  Logger.log('✅ Test complete. Check logs above.');
}

/**
 * Get execution logs for the last 24 hours
 * Run this to see ping history
 */
function viewLogs() {
  const logs = Logger.getLog();
  Logger.log('📊 Recent Ping Logs:');
  Logger.log(logs);
}

/**
 * Optional: Create a time-based trigger programmatically
 * Run this once to set up the trigger automatically
 */
function createTrigger() {
  // Delete existing triggers first to avoid duplicates
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => {
    if (trigger.getHandlerFunction() === 'pingBackend') {
      ScriptApp.deleteTrigger(trigger);
    }
  });
  
  // Create new trigger: Run every 10 minutes
  ScriptApp.newTrigger('pingBackend')
    .timeBased()
    .everyMinutes(10)
    .create();
  
  Logger.log('✅ Trigger created: pingBackend will run every 10 minutes');
}

/**
 * Delete all triggers
 * Run this if you want to stop the pings
 */
function deleteTriggers() {
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => {
    ScriptApp.deleteTrigger(trigger);
  });
  Logger.log('🗑️ All triggers deleted');
}
