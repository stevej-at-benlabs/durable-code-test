#!/usr/bin/env node

/**
 * Simple HTTP check to see if the dev server is responding
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