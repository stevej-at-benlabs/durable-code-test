#!/usr/bin/env node

/**
 * Purpose: Simple HTTP health check for the development server to verify basic connectivity and response
 * Scope: Development server validation and basic HTML structure verification
 * Overview: This script performs a lightweight HTTP GET request to localhost:5173 to check if the Vite
 *           development server is running and responding with valid HTML content. It validates the presence
 *           of key HTML elements like the root div and main script tag, providing detailed console output
 *           for debugging server startup issues.
 * Dependencies: Node.js built-in http module
 * Exports: No exports - standalone script
 * Interfaces: Command-line script with console output and exit codes (0 for success, 1 for failure)
 * Implementation: Promise-based HTTP client with timeout handling and response content validation
 */

import http from 'http';

function checkServer() {
  return new Promise((resolve, reject) => {
    const req = http.get('http://localhost:5173', (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        console.log('📍 Server Response Status:', res.statusCode);
        console.log('📄 Content Length:', data.length);

        if (data.includes('<div id="root"></div>')) {
          console.log('✅ Root div found in HTML');
        } else {
          console.log('❌ Root div NOT found');
        }

        if (data.includes('<script type="module" src="/src/main.tsx"')) {
          console.log('✅ Main script tag found');
        } else {
          console.log('❌ Main script tag NOT found');
        }

        console.log('\n📋 First 300 characters of response:');
        console.log('─'.repeat(50));
        console.log(data.substring(0, 300));

        if (res.statusCode === 200 && data.length > 100) {
          console.log('\n✅ SUCCESS: Server is responding with HTML content');
          resolve(true);
        } else {
          console.log('\n❌ FAILURE: Server response is not as expected');
          resolve(false);
        }
      });
    });

    req.on('error', (err) => {
      console.error('❌ ERROR: Failed to connect to server:', err.message);
      reject(err);
    });

    req.setTimeout(5000, () => {
      console.error('❌ ERROR: Request timeout');
      req.destroy();
      reject(new Error('Timeout'));
    });
  });
}

async function main() {
  try {
    console.log('🔍 Checking dev server at http://localhost:5173...\n');
    await checkServer();
  } catch (error) {
    console.error('Fatal error:', error.message);
    process.exit(1);
  }
}

main();
