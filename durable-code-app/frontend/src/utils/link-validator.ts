/**
 * Purpose: Facade for link validation functionality, combining all services
 * Scope: Unified interface for link validation, categorization, and reporting
 * Created: 2025-09-12
 * Updated: 2025-09-16
 * Author: Development Team
 * Version: 2.0
 *
 * This file acts as a facade that combines and re-exports functionality from:
 * - LinkValidationService: HTTP validation logic
 * - LinkCategorizationService: Link classification logic
 * - LinkReportService: Report generation logic
 * - LinkExtractionService: DOM parsing (already separate)
 * - LinkRegistry: Registry management (already separate)
 */

// Re-export validation functionality
export {
  LinkValidationService,
  validateLink,
  validateLinks,
  type LinkValidationResult,
  type LinkValidationOptions,
} from './LinkValidationService';

// Re-export categorization functionality
export {
  LinkCategorizationService,
  HttpLinkCategorizer,
  RelativeLinkCategorizer,
  HashLinkCategorizer,
  ProtocolLinkCategorizer,
  categorizeLinks,
  type LinkCategorizer,
  type CategorizedLinks,
} from './LinkCategorizationService';

// Re-export report functionality
export {
  LinkReportService,
  SummaryReportBuilder,
  DetailedReportBuilder,
  CsvReportBuilder,
  createLinkReportSummary,
  type LinkReportSummary,
  type DetailedLinkReport,
  type ReportBuilder,
} from './LinkReportService';

// Import services for facade operations
import { LinkValidationService } from './LinkValidationService';
import type {
  LinkValidationOptions,
  LinkValidationResult,
} from './LinkValidationService';
import { categorizeLinks } from './LinkCategorizationService';
import { CompositeLinkExtractor } from './LinkExtractionService';
import type { LinkRegistry } from './LinkRegistryInterfaces';

/**
 * Extracts all links from a DOM element
 */
export function extractLinksFromElement(element: HTMLElement): string[] {
  const extractor = new CompositeLinkExtractor();
  return extractor.extractAllLinks(element);
}

/**
 * Generates a validation report for all links in an element
 * This is a facade method that combines multiple services
 */
export async function generateLinkReport(
  element: HTMLElement,
  options: LinkValidationOptions = {},
): Promise<{
  totalLinks: number;
  validLinks: number;
  brokenLinks: number;
  results: LinkValidationResult[];
  categories: ReturnType<typeof categorizeLinks>;
}> {
  // Extract links from DOM
  const links = extractLinksFromElement(element);

  // Categorize links
  const categories = categorizeLinks(links);

  // Validate links
  const validationService = new LinkValidationService();
  const results = await validationService.validateLinks(links, options);

  // Generate summary
  const validLinks = results.filter((r) => r.isValid).length;
  const brokenLinks = results.filter((r) => !r.isValid).length;

  return {
    totalLinks: links.length,
    validLinks,
    brokenLinks,
    results,
    categories,
  };
}

// Registry functionality (keeping existing implementations for backward compatibility)

/**
 * Registry for React route links
 */
export class ReactRouteRegistry implements LinkRegistry {
  private routes: string[] = ['standards'];

  getLinks(): string[] {
    return [...this.routes];
  }

  addLink(link: string): void {
    if (!this.routes.includes(link)) {
      this.routes.push(link);
    }
  }

  removeLink(link: string): void {
    this.routes = this.routes.filter((route) => route !== link);
  }
}

/**
 * Registry for diagram files
 */
export class DiagramRegistry implements LinkRegistry {
  private diagrams: string[] = [
    'diagrams/durable-code-flow.html',
    'diagrams/ai-review-sequence.html',
    'diagrams/implementation-plan.html',
  ];

  getLinks(): string[] {
    return [...this.diagrams];
  }

  addLink(link: string): void {
    if (!this.diagrams.includes(link)) {
      this.diagrams.push(link);
    }
  }

  removeLink(link: string): void {
    this.diagrams = this.diagrams.filter((diagram) => diagram !== link);
  }
}

/**
 * Composite registry that manages multiple link registries
 */
export class ExpectedLinksRegistry {
  private registries: LinkRegistry[] = [];

  constructor(registries: LinkRegistry[] = []) {
    this.registries =
      registries.length > 0
        ? registries
        : [new ReactRouteRegistry(), new DiagramRegistry()];
  }

  addRegistry(registry: LinkRegistry): void {
    this.registries.push(registry);
  }

  getAllLinks(): string[] {
    const allLinks: string[] = [];
    this.registries.forEach((registry) => {
      allLinks.push(...registry.getLinks());
    });
    return allLinks;
  }

  addLinkToRegistry(registryIndex: number, link: string): void {
    if (this.registries[registryIndex]) {
      this.registries[registryIndex].addLink(link);
    }
  }
}

/**
 * Default expected links registry instance
 */
export const defaultExpectedLinksRegistry = new ExpectedLinksRegistry();

/**
 * Gets all expected public links from the registry system
 */
export function getExpectedPublicLinks(): string[] {
  return defaultExpectedLinksRegistry.getAllLinks();
}

/**
 * Validates that all expected public links exist
 */
export async function validateExpectedLinks(
  options: LinkValidationOptions = {},
  registry: ExpectedLinksRegistry = defaultExpectedLinksRegistry,
): Promise<{
  allValid: boolean;
  results: LinkValidationResult[];
  missing: string[];
}> {
  const validationService = new LinkValidationService();
  const linksToValidate = registry.getAllLinks();
  const results = await validationService.validateLinks(linksToValidate, options);
  const missing = results.filter((r) => !r.isValid).map((r) => r.url);

  return {
    allValid: results.every((r) => r.isValid),
    results,
    missing,
  };
}
