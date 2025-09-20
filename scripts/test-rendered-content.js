const { execSync } = require('child_process');

function checkRenderedContent() {
  try {
    // Use curl to check if we get any meaningful content
    const response = execSync('curl -s http://localhost:5173', { encoding: 'utf8' });

    console.log('🔍 Checking rendered content...');
    console.log('Response length:', response.length);

    // Check if we have basic HTML structure
    const hasRoot = response.includes('<div id="root">');
    const hasMainScript = response.includes('/src/main.tsx');
    const hasViteClient = response.includes('/@vite/client');

    console.log('✅ Has root div:', hasRoot);
    console.log('✅ Has main script:', hasMainScript);
    console.log('✅ Has vite client:', hasViteClient);

    // Show first part of response
    console.log('\n📄 First 500 chars of response:');
    console.log('─'.repeat(50));
    console.log(response.substring(0, 500));

    if (hasRoot && (hasMainScript || hasViteClient)) {
      console.log('\n✅ SUCCESS: App structure looks correct');
      return true;
    } else {
      console.log('\n❌ FAILURE: Missing expected HTML structure');
      return false;
    }

  } catch (error) {
    console.error('❌ ERROR:', error.message);
    return false;
  }
}

// Run check
const success = checkRenderedContent();
process.exit(success ? 0 : 1);
