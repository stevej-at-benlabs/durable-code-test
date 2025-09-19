/**
 * Purpose: Custom hook for managing infrastructure feature data and state
 * Scope: Infrastructure tab data provider with error handling and loading states
 * Overview: React hook that provides all infrastructure-related data including
 *     infrastructure items, folder structure, make targets, stats, and action links.
 *     Handles loading states and error management for the infrastructure feature.
 * Dependencies: React (useState, useEffect, useMemo), infrastructure types
 * Exports: useInfrastructure hook function
 * Props/Interfaces: No parameters, returns UseInfrastructureReturn interface
 * State/Behavior: Manages loading state, error state, and static data provision
 */

import { useEffect, useMemo, useState } from 'react';
import type {
  ActionLink,
  FolderItem,
  InfrastructureItem,
  InfrastructureStats,
  MakeTarget,
  UseInfrastructureReturn,
} from '../types/infrastructure.types';

export function useInfrastructure(): UseInfrastructureReturn {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  // Infrastructure items data
  const infrastructureItems = useMemo(
    (): InfrastructureItem[] => [
      {
        id: 'custom-linters',
        icon: '🔧',
        title: 'Custom Linters',
        description:
          'Enforce your specific standards automatically - from logging practices to file organization, catching violations before they enter the codebase',
        badge: 'Critical',
        category: 'quality',
      },
      {
        id: 'make-targets',
        icon: '⚙️',
        title: 'Make Targets',
        description:
          'Reliable, repeatable automation that produces consistent results regardless of environment or developer',
        badge: 'Critical',
        category: 'automation',
      },
      {
        id: 'quality-gates',
        icon: '🔒',
        title: 'Quality Gates',
        description:
          'Pre-commit hooks, merge protection, and CI/CD checks creating multiple layers of defense',
        badge: 'Critical',
        category: 'quality',
      },
      {
        id: 'merge-protection',
        icon: '🛡️',
        title: 'Merge Protection',
        description:
          'Branch protection rules and CI/CD status checks preventing broken code from reaching main',
        badge: 'Critical',
        category: 'security',
      },
      {
        id: 'automated-reviews',
        icon: '🔍',
        title: 'Automated PR Reviews',
        description:
          'AI-powered code reviews ensuring strict standard adherence with greater detail and consistency than humans',
        badge: 'Critical',
        category: 'ai',
      },
      {
        id: 'claude-commands',
        icon: '🤖',
        title: 'Claude Commands',
        description:
          'Custom AI commands like /new-code, /ask, and /solid with template-driven generation',
        badge: 'Critical',
        category: 'ai',
      },
      {
        id: 'lightweight-lookups',
        icon: '📑',
        title: 'Lightweight Look-ups',
        description:
          'Quick-access indices and metadata that AI can rapidly parse - .ai/index.json, file headers, and structured navigation',
        badge: 'Critical',
        category: 'ai',
      },
    ],
    [],
  );

  // Folder structure data
  const folderStructure = useMemo(
    (): FolderItem[] => [
      {
        id: 'ai-root',
        type: 'folder',
        name: '.ai/',
        icon: '📦',
        depth: 0,
      },
      {
        id: 'index-json',
        type: 'file',
        name: 'index.json',
        icon: '📋',
        description: 'Quick navigation for AI agents',
        depth: 1,
      },
      {
        id: 'index-expanded',
        type: 'file',
        name: 'index_expanded.md',
        icon: '📄',
        description: 'Comprehensive AI documentation',
        depth: 1,
      },
      {
        id: 'docs-folder',
        type: 'folder',
        name: 'docs/',
        icon: '📁',
        description: 'Development standards',
        depth: 1,
      },
      {
        id: 'standards-md',
        type: 'file',
        name: 'STANDARDS.md',
        icon: '📝',
        depth: 2,
      },
      {
        id: 'file-header-standards',
        type: 'file',
        name: 'FILE_HEADER_STANDARDS.md',
        icon: '📝',
        depth: 2,
      },
      {
        id: 'css-layout',
        type: 'file',
        name: 'CSS_LAYOUT_STABILITY.md',
        icon: '📝',
        depth: 2,
      },
      {
        id: 'branch-protection',
        type: 'file',
        name: 'BRANCH_PROTECTION.md',
        icon: '📝',
        depth: 2,
        isLast: true,
      },
      {
        id: 'features-folder',
        type: 'folder',
        name: 'features/',
        icon: '📁',
        description: 'Feature documentation',
        depth: 1,
      },
      {
        id: 'design-linters-md',
        type: 'file',
        name: 'design-linters.md',
        icon: '🔧',
        depth: 2,
      },
      {
        id: 'web-application-md',
        type: 'file',
        name: 'web-application.md',
        icon: '🌐',
        depth: 2,
      },
      {
        id: 'development-tooling-md',
        type: 'file',
        name: 'development-tooling.md',
        icon: '⚙️',
        depth: 2,
      },
      {
        id: 'claude-integration-md',
        type: 'file',
        name: 'claude-integration.md',
        icon: '🤖',
        depth: 2,
      },
      {
        id: 'testing-framework-md',
        type: 'file',
        name: 'testing-framework.md',
        icon: '🧪',
        depth: 2,
        isLast: true,
      },
      {
        id: 'howto-folder',
        type: 'folder',
        name: 'howto/',
        icon: '📁',
        description: 'Step-by-step guides',
        depth: 1,
      },
      {
        id: 'run-tests-md',
        type: 'file',
        name: 'run-tests.md',
        icon: '🧪',
        depth: 2,
      },
      {
        id: 'run-linting-md',
        type: 'file',
        name: 'run-linting.md',
        icon: '🔍',
        depth: 2,
      },
      {
        id: 'setup-development-md',
        type: 'file',
        name: 'setup-development.md',
        icon: '🛠️',
        depth: 2,
      },
      {
        id: 'deploy-application-md',
        type: 'file',
        name: 'deploy-application.md',
        icon: '🚀',
        depth: 2,
      },
      {
        id: 'debug-issues-md',
        type: 'file',
        name: 'debug-issues.md',
        icon: '🐛',
        depth: 2,
      },
      {
        id: 'debug-with-tests-md',
        type: 'file',
        name: 'debug-with-tests-and-logging.md',
        icon: '🔬',
        depth: 2,
        isLast: true,
      },
      {
        id: 'templates-folder',
        type: 'folder',
        name: 'templates/',
        icon: '📁',
        description: 'Production-ready templates',
        depth: 1,
        isLast: true,
      },
      {
        id: 'linting-rule-template',
        type: 'file',
        name: 'linting-rule.py.template',
        icon: '🔧',
        depth: 2,
        parentIsLast: true,
      },
      {
        id: 'react-component-template',
        type: 'file',
        name: 'react-component.tsx.template',
        icon: '⚛️',
        depth: 2,
        parentIsLast: true,
      },
      {
        id: 'web-tab-template',
        type: 'file',
        name: 'web-tab.tsx.template',
        icon: '📑',
        depth: 2,
        parentIsLast: true,
      },
      {
        id: 'fastapi-endpoint-template',
        type: 'file',
        name: 'fastapi-endpoint.py.template',
        icon: '🌐',
        depth: 2,
        parentIsLast: true,
      },
      {
        id: 'test-suite-template',
        type: 'file',
        name: 'test-suite.py.template',
        icon: '🧪',
        depth: 2,
        parentIsLast: true,
      },
      {
        id: 'workflow-template',
        type: 'file',
        name: 'workflow.html.template',
        icon: '📊',
        depth: 2,
        isLast: true,
        parentIsLast: true,
      },
    ],
    [],
  );

  // Make targets data
  const makeTargets = useMemo(
    (): MakeTarget[] => [
      {
        name: 'test',
        icon: '🧪',
        description: 'Same tests, same environment, every time',
        category: 'testing',
        importance: 'critical',
      },
      {
        name: 'lint-all',
        icon: '🔍',
        description: 'Consistent quality checks across machines',
        category: 'linting',
        importance: 'critical',
      },
      {
        name: 'build',
        icon: '🏗️',
        description: 'Identical builds from identical inputs',
        category: 'building',
        importance: 'critical',
      },
      {
        name: 'deploy',
        icon: '🚀',
        description: 'Predictable deployment every time',
        category: 'deployment',
        importance: 'important',
      },
      {
        name: 'setup',
        icon: '🔧',
        description: 'Environment setup: deterministic',
        category: 'deployment',
        importance: 'important',
      },
      {
        name: 'validate',
        icon: '📊',
        description: 'Quality gates with known outcomes',
        category: 'testing',
        importance: 'important',
      },
      {
        name: 'clean',
        icon: '🧹',
        description: 'Reset to known clean state',
        category: 'maintenance',
        importance: 'utility',
      },
      {
        name: 'format',
        icon: '📋',
        description: 'Code formatting: same result always',
        category: 'linting',
        importance: 'utility',
      },
      {
        name: 'security-scan',
        icon: '🔒',
        description: 'Reproducible security analysis',
        category: 'testing',
        importance: 'important',
      },
      {
        name: 'benchmark',
        icon: '📈',
        description: 'Performance metrics: consistent baseline',
        category: 'testing',
        importance: 'utility',
      },
    ],
    [],
  );

  // Stats data
  const stats = useMemo(
    (): InfrastructureStats => ({
      makeTargets: 40,
      linterCategories: 5,
      codeTemplates: 6,
      dockerCoverage: '100%',
    }),
    [],
  );

  // Action links data
  const actionLinks = useMemo(
    (): ActionLink[] => [
      {
        id: 'ai-repository',
        url: 'https://github.com/stevej-at-benlabs/durable-code-test/tree/main/.ai',
        text: 'Explore .ai Repository',
        icon: '📂',
        type: 'primary',
        description: 'Browse the AI documentation structure',
      },
      {
        id: 'make-targets',
        url: 'https://github.com/stevej-at-benlabs/durable-code-test/blob/main/Makefile.lint',
        text: 'View Make Targets',
        icon: '🔧',
        type: 'secondary',
        description: 'See automation targets in action',
      },
      {
        id: 'custom-linters',
        url: 'https://github.com/stevej-at-benlabs/durable-code-test/tree/main/tools/design_linters',
        text: 'Custom Linters',
        icon: '🎯',
        type: 'secondary',
        description: 'Explore the linting framework',
      },
      {
        id: 'precommit-config',
        url: 'https://github.com/stevej-at-benlabs/durable-code-test/blob/main/.pre-commit-config.yaml',
        text: 'Pre-commit Config',
        icon: '🔒',
        type: 'secondary',
        description: 'See quality gates configuration',
      },
    ],
    [],
  );

  // Simulate loading effect
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Simulate brief loading for realistic UX
        await new Promise((resolve) => setTimeout(resolve, 100));

        setLoading(false);
      } catch (err) {
        const error =
          err instanceof Error ? err : new Error('Failed to load infrastructure data');
        setError(error);
        setLoading(false);
      }
    };

    loadData();
  }, []);

  return {
    infrastructureItems,
    folderStructure,
    makeTargets,
    stats,
    actionLinks,
    loading,
    error,
  };
}
