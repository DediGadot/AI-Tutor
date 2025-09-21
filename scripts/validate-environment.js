#!/usr/bin/env node

/**
 * Environment validation script for Hebrew AI Tutor
 * Validates Node.js version, dependencies, and critical components
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const requiredNodeVersion = 18;
const criticalFiles = [
  'package.json',
  'next.config.js',
  'jest.config.js',
  'src/components/CodeEditor.tsx',
  'src/components/PreviewPanel.tsx',
  'src/components/TestRunner.tsx',
  'src/components/Speech/TTSProvider.tsx',
];

console.log('🔍 Validating Hebrew AI Tutor Environment...\n');

// Check Node.js version
const nodeVersion = parseInt(process.version.match(/v(\d+)/)[1]);
if (nodeVersion < requiredNodeVersion) {
  console.error(`❌ Node.js ${requiredNodeVersion}+ required, found ${nodeVersion}`);
  process.exit(1);
} else {
  console.log(`✅ Node.js ${nodeVersion} (>= ${requiredNodeVersion})`);
}

// Check critical files
for (const file of criticalFiles) {
  if (fs.existsSync(file)) {
    console.log(`✅ ${file}`);
  } else {
    console.error(`❌ Missing critical file: ${file}`);
    process.exit(1);
  }
}

// Check package.json dependencies
const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
const requiredDeps = {
  'next': '15',
  'react': '18',
  '@testing-library/react': '16',
  'jest': '29',
  'typescript': '5',
};

for (const [dep, minVersion] of Object.entries(requiredDeps)) {
  const installed = packageJson.dependencies?.[dep] || packageJson.devDependencies?.[dep];
  if (installed) {
    console.log(`✅ ${dep}: ${installed}`);
  } else {
    console.error(`❌ Missing dependency: ${dep}`);
    process.exit(1);
  }
}

// Test basic compilation
try {
  console.log('\n🔧 Testing TypeScript compilation...');
  execSync('npx tsc --noEmit --skipLibCheck', { stdio: 'inherit' });
  console.log('✅ TypeScript compilation successful');
} catch (error) {
  console.error('❌ TypeScript compilation failed');
  process.exit(1);
}

// Test Jest configuration
try {
  console.log('\n🧪 Testing Jest configuration...');
  execSync('npm test -- --passWithNoTests', { stdio: 'inherit' });
  console.log('✅ Jest configuration valid');
} catch (error) {
  console.error('❌ Jest configuration invalid');
  process.exit(1);
}

console.log('\n🎉 Environment validation complete! All systems ready.\n');

// Display quick statistics
const srcFiles = execSync('find src -name "*.tsx" -o -name "*.ts" | wc -l').toString().trim();
const testFiles = execSync('find __tests__ -name "*.test.*" | wc -l').toString().trim();

console.log('📊 Project Statistics:');
console.log(`   • Source files: ${srcFiles}`);
console.log(`   • Test files: ${testFiles}`);
console.log(`   • Components: ${criticalFiles.filter(f => f.includes('components')).length}`);
console.log('');