#!/usr/bin/env node

/**
 * Purpose: Comprehensive page content validation using browser automation to verify React app rendering
 * Scope: End-to-end browser testing for React application content and DOM structure validation
 * Overview: This script uses Playwright to launch a headless Chromium browser, navigate to the development
 *           server, and perform detailed checks on the rendered DOM content. It validates both HTML structure
 *           and text content, checks for specific UI elements (headers, navigation, sections), and provides
 *           comprehensive reporting on page rendering success or failure.
 * Dependencies: Playwright (chromium browser automation library)
 * Exports: No exports - standalone script
 * Interfaces: Command-line script with detailed console logging and exit codes for CI/CD integration
 * Implementation: Async/await pattern with Playwright browser automation, DOM querying, and element validation
 */

import { chromium } from 'playwright';

async function checkPageContent() {
  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  try {
    const context = await browser.newContext();
    const page = await context.newPage();

    // Listen for console messages
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.error('Browser console error:', msg.text());
      }
    });

    // Navigate to the dev server
    console.log('📍 Navigating to http://localhost:5173...');
    await page.goto('http://localhost:5173', {
      waitUntil: 'networkidle',
      timeout: 10000
    });

    // Wait a bit for React to fully render
    await page.waitForTimeout(2000);

    // Get the root element
    const rootElement = await page.$('#root');

    if (!rootElement) {
      console.error('❌ ERROR: No root element found!');
      process.exit(1);
    }

    // Get the inner HTML and text content
    const innerHTML = await rootElement.innerHTML();
    const innerText = await rootElement.innerText();

    console.log('\n📋 Root Element Content Check:');
    console.log('─'.repeat(50));

    if (innerHTML && innerHTML.trim().length > 0) {
      console.log('✅ HTML Content: Found');
      console.log(`   Length: ${innerHTML.length} characters`);

      // Show first 200 chars of HTML
      console.log('\n📄 First 200 chars of HTML:');
      console.log(innerHTML.substring(0, 200) + '...');
    } else {
      console.log('❌ HTML Content: EMPTY');
    }

    if (innerText && innerText.trim().length > 0) {
      console.log('\n✅ Text Content: Found');
      console.log(`   Length: ${innerText.length} characters`);

      // Show first 200 chars of text
      console.log('\n📝 First 200 chars of text:');
      console.log(innerText.substring(0, 200) + '...');
    } else {
      console.log('❌ Text Content: EMPTY');
    }

    // Check for specific elements that should exist
    console.log('\n🔍 Element Checks:');
    console.log('─'.repeat(50));

    const checks = [
      { selector: 'h1', name: 'Main heading' },
      { selector: 'header', name: 'Header' },
      { selector: 'main', name: 'Main content' },
      { selector: 'footer', name: 'Footer' },
      { selector: '[class*="hero"]', name: 'Hero section' },
      { selector: '[class*="tab"]', name: 'Tab navigation' }
    ];

    for (const check of checks) {
      const element = await page.$(check.selector);
      if (element) {
        console.log(`✅ ${check.name}: Found`);
      } else {
        console.log(`❌ ${check.name}: Not found`);
      }
    }

    // Final verdict
    console.log('\n📊 Final Result:');
    console.log('─'.repeat(50));

    if (innerHTML && innerHTML.length > 100 && innerText && innerText.length > 50) {
      console.log('✅ SUCCESS: Page is rendering content properly!');
      process.exit(0);
    } else {
      console.log('❌ FAILURE: Page appears to be blank or broken!');
      process.exit(1);
    }

  } catch (error) {
    console.error('❌ Error checking page:', error.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

// Run the check
checkPageContent().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
