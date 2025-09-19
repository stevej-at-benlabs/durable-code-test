/**
 * Purpose: Custom React hook for managing building feature data and state
 * Scope: Development tools, commands, templates management
 * Overview: Provides data and utilities for the building feature components
 * Dependencies: React, building types
 * Exports: useBuilding custom hook
 * Interfaces: Uses types from building.types.ts
 * Implementation: Returns building-related data organized by sections
 */

import { useMemo } from 'react';
import type {
  AiCommand,
  Capability,
  Command,
  HowToGuide,
  Standard,
  Template,
} from '../types/building.types';

const COMMANDS: Command[] = [
  {
    id: 'new-code',
    icon: '🧩',
    type: 'Generation',
    syntax:
      '$ /new-code Create a user authentication system with login and registration',
    description: 'Generate production-ready code with proper structure and standards',
  },
  {
    id: 'solid',
    icon: '🎯',
    type: 'Quality',
    syntax: '$ /solid',
    description: 'Run parallel AI agents to check SOLID principle violations',
  },
  {
    id: 'done',
    icon: '✅',
    type: 'Workflow',
    syntax: '$ /done [with merge]',
    description: 'Complete workflow with optional auto-merge after all checks pass',
  },
  {
    id: 'ask',
    icon: '❓',
    type: 'Analysis',
    syntax: '$ /ask How does the authentication work?',
    description: 'Ask questions and get AI-powered insights about your codebase',
  },
];

const CAPABILITIES: Capability[] = [
  {
    id: 'component',
    icon: '🧩',
    type: 'Component',
    syntax:
      '/new-code Create a user profile component with avatar, bio, and contact information',
    description:
      'Generate React/Vue/Angular components with props, state, and lifecycle',
  },
  {
    id: 'service',
    icon: '🔧',
    type: 'Service',
    syntax: '/new-code Build an authentication service with JWT token management',
    description: 'Create service layers with dependency injection and error handling',
  },
  {
    id: 'test',
    icon: '🧪',
    type: 'Test',
    syntax: '/new-code Write comprehensive tests for the payment processing module',
    description: 'Generate test suites with mocks, fixtures, and coverage setup',
  },
  {
    id: 'api',
    icon: '🗄️',
    type: 'API',
    syntax:
      '/new-code Implement a REST API for managing user subscriptions and billing',
    description: 'Scaffold REST/GraphQL endpoints with validation and middleware',
  },
  {
    id: 'database',
    icon: '🗃️',
    type: 'Database',
    syntax: '/new-code Design database models for an e-commerce product catalog',
    description: 'Create database schemas, migrations, and ORM models',
  },
  {
    id: 'ui',
    icon: '🎨',
    type: 'UI/UX',
    syntax: '/new-code Build a responsive dashboard with charts and data visualization',
    description: 'Generate styled components with responsive design and accessibility',
  },
];

const AI_COMMANDS: AiCommand[] = [
  {
    id: 'solid',
    icon: '🎯',
    name: '/solid',
    description: 'Parallel AI agents analyze SOLID principle violations',
    features: ['5 AI Agents', 'Parallel Analysis', 'Smart Reports'],
    modes: [
      { syntax: '/solid', description: 'Current branch only' },
      { syntax: '/solid all code', description: 'Comprehensive analysis' },
    ],
  },
  {
    id: 'done',
    icon: '✅',
    name: '/done',
    description:
      'Complete workflow automation from commit to PR with optional auto-merge',
    features: ['Auto Commit', 'Quality Checks', 'Auto Merge'],
    modes: [
      { syntax: '/done', description: 'Create PR, wait for review' },
      { syntax: '/done with merge', description: 'Auto-merge after all checks pass' },
    ],
  },
];

const TEMPLATES: Template[] = [
  {
    id: 'linting',
    icon: '🔧',
    filename: 'linting-rule.py',
    description: 'Create custom design linting rules for code quality enforcement',
  },
  {
    id: 'react',
    icon: '⚛️',
    filename: 'react-component.tsx',
    description: 'Generate React components with proper typing and structure',
  },
  {
    id: 'web-tab',
    icon: '🗂️',
    filename: 'web-tab.tsx',
    description: 'Build new web application tabs with consistent UI patterns',
  },
  {
    id: 'fastapi',
    icon: '🚀',
    filename: 'fastapi-endpoint.py',
    description: 'Scaffold FastAPI endpoints with validation and error handling',
  },
  {
    id: 'test',
    icon: '🧪',
    filename: 'test-suite.py',
    description: 'Create comprehensive test suites with fixtures and coverage',
  },
  {
    id: 'websocket',
    icon: '🔌',
    filename: 'websocket-endpoint.py',
    description: 'Implement WebSocket endpoints for real-time communication',
  },
  {
    id: 'workflow',
    icon: '📋',
    filename: 'workflow.html',
    description: 'Document development workflows with interactive HTML templates',
  },
];

const HOWTO_GUIDES: HowToGuide[] = [
  {
    id: 'debugging',
    icon: '🐛',
    title: 'Complete Debugging Guide',
    description:
      'Comprehensive strategies for troubleshooting and debugging with AI assistance',
  },
  {
    id: 'linter',
    icon: '✨',
    title: 'Create Custom Linter',
    description:
      'Build your own design linting rules to enforce project-specific standards',
  },
  {
    id: 'deploy',
    icon: '🚀',
    title: 'Deploy Application',
    description: 'Step-by-step deployment guide for production environments',
  },
  {
    id: 'github',
    icon: '🔀',
    title: 'GitHub Merge Workflow',
    description: 'Automated PR creation and merge workflows with AI validation',
  },
  {
    id: 'linting',
    icon: '🔍',
    title: 'Run Linting',
    description: 'Execute comprehensive linting checks across your entire codebase',
  },
  {
    id: 'tests',
    icon: '🧪',
    title: 'Run Tests',
    description: 'Testing strategies and commands for different test suites',
  },
  {
    id: 'setup',
    icon: '🛠️',
    title: 'Setup Development',
    description: 'Initialize your development environment for AI-assisted coding',
  },
];

const STANDARDS: Standard[] = [
  {
    id: 'conventions',
    icon: '📏',
    title: 'Coding Conventions',
    description:
      'Consistent naming, formatting, and structure per .ai/docs/STANDARDS.md',
  },
  {
    id: 'architecture',
    icon: '🏗️',
    title: 'Architecture Patterns',
    description: 'Approved design patterns and practices documented in standards',
  },
  {
    id: 'quality',
    icon: '✅',
    title: 'Quality Rules',
    description: 'Comprehensive linting, type safety, and documentation requirements',
  },
  {
    id: 'practices',
    icon: '🚀',
    title: 'Best Practices',
    description: 'Security, performance, and maintainability guidelines',
  },
];

export function useBuilding() {
  return useMemo(
    () => ({
      commands: COMMANDS,
      capabilities: CAPABILITIES,
      aiCommands: AI_COMMANDS,
      templates: TEMPLATES,
      howToGuides: HOWTO_GUIDES,
      standards: STANDARDS,
    }),
    [],
  );
}
