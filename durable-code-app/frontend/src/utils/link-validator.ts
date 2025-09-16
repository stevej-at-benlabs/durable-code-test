/**
 * Purpose: Utility functions for validating links and external resources
 * Scope: Link checking, resource validation, and broken link detection
 * Created: 2025-09-12
 * Updated: 2025-09-12
 * Author: Development Team
 * Version: 1.0
 */

import {
  UrlNormalizer,
  HttpRequestService,
  ValidationResultBuilder,
} from './HttpRequestService';
import type { ValidationResult } from './HttpRequestService';
import { CompositeLinkExtractor } from './LinkExtractionService';
import type { LinkRegistry } from './LinkRegistryInterfaces';

export type LinkValidationResult = ValidationResult;

export interface LinkValidationOptions {
  timeout?: number;
  followRedirects?: boolean;
  checkHeaders?: boolean;
}

/**
 * Validates a single link by making an HTTP request
 */
export async function validateLink(
  url: string,
  options: LinkValidationOptions = {},
): Promise<LinkValidationResult> {
  const startTime = Date.now();
  const httpService = new HttpRequestService();

  try {
    const fullUrl = UrlNormalizer.normalizeUrl(url);
    const response = await httpService.makeRequest(fullUrl, options);

    return ValidationResultBuilder.createSuccessResult(url, response);
  } catch (error) {
    const responseTime = Date.now() - startTime;
    return ValidationResultBuilder.createErrorResult(url, error, responseTime);
  }
}

/**
 * Validates multiple links concurrently
 */
export async function validateLinks(
  urls: string[],
  options: LinkValidationOptions = {},
): Promise<LinkValidationResult[]> {
  const validationPromises = urls.map((url) => validateLink(url, options));
  return Promise.all(validationPromises);
}

/**
 * Extracts all links from a DOM element
 */
export function extractLinksFromElement(element: HTMLElement): string[] {
  const extractor = new CompositeLinkExtractor();
  return extractor.extractAllLinks(element);
}

/**
 * Link categorizer interface for extensible link classification
 */
export interface LinkCategorizer {
  categorize(url: string): string[];
}

/**
 * Default implementation for HTTP/HTTPS link categorization
 */
export class HttpLinkCategorizer implements LinkCategorizer {
  categorize(url: string): string[] {
    const categories: string[] = [];

    if (url.startsWith('http://') || url.startsWith('https://')) {
      categories.push('absolute');
      if (url.includes(window.location.hostname)) {
        categories.push('internal');
      } else {
        categories.push('external');
      }
    }

    return categories;
  }
}

/**
 * Relative link categorizer
 */
export class RelativeLinkCategorizer implements LinkCategorizer {
  categorize(url: string): string[] {
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      return ['relative', 'internal'];
    }
    return [];
  }
}

/**
 * Link categorization service that supports multiple categorizers
 */
export class LinkCategorizationService {
  private categorizers: LinkCategorizer[] = [];

  constructor(categorizers: LinkCategorizer[] = []) {
    this.categorizers =
      categorizers.length > 0
        ? categorizers
        : [new HttpLinkCategorizer(), new RelativeLinkCategorizer()];
  }

  addCategorizer(categorizer: LinkCategorizer): void {
    this.categorizers.push(categorizer);
  }

  categorizeLinks(urls: string[]): {
    internal: string[];
    external: string[];
    relative: string[];
    absolute: string[];
  } {
    const internal: string[] = [];
    const external: string[] = [];
    const relative: string[] = [];
    const absolute: string[] = [];

    urls.forEach((url) => {
      const allCategories = new Set<string>();

      // Apply all categorizers and collect unique categories
      this.categorizers.forEach((categorizer) => {
        const categories = categorizer.categorize(url);
        categories.forEach((category) => allCategories.add(category));
      });

      // Sort URLs into appropriate arrays based on categories
      if (allCategories.has('internal')) internal.push(url);
      if (allCategories.has('external')) external.push(url);
      if (allCategories.has('relative')) relative.push(url);
      if (allCategories.has('absolute')) absolute.push(url);
    });

    return { internal, external, relative, absolute };
  }
}

/**
 * Backward compatibility function - uses the new service internally
 */
export function categorizeLinks(urls: string[]): {
  internal: string[];
  external: string[];
  relative: string[];
  absolute: string[];
} {
  const service = new LinkCategorizationService();
  return service.categorizeLinks(urls);
}

/**
 * Generates a validation report for all links
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
  const links = extractLinksFromElement(element);
  const categories = categorizeLinks(links);
  const results = await validateLinks(links, options);

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

/**
 * Interface for building different types of reports
 */
export interface ReportBuilder {
  buildSummary(results: LinkValidationResult[]): any;
}

/**
 * Default summary report builder
 */
export class SummaryReportBuilder implements ReportBuilder {
  buildSummary(results: LinkValidationResult[]) {
    const total = results.length;
    const valid = results.filter((r) => r.isValid).length;
    const broken = results.filter((r) => !r.isValid).length;

    return {
      summary: {
        total,
        valid,
        broken,
      },
      results,
    };
  }
}

/**
 * Service for creating link reports with extensible builders
 */
export class LinkReportService {
  private builder: ReportBuilder;

  constructor(builder?: ReportBuilder) {
    this.builder = builder || new SummaryReportBuilder();
  }

  setBuilder(builder: ReportBuilder): void {
    this.builder = builder;
  }

  createReport(results: LinkValidationResult[]) {
    return this.builder.buildSummary(results);
  }
}

/**
 * Creates a link report summary from validation results
 * @deprecated Use LinkReportService for new code
 */
export function createLinkReportSummary(results: LinkValidationResult[]) {
  const service = new LinkReportService();
  return service.createReport(results);
}

/**
 * Link registry interface for managing expected links
 * @deprecated Use ReadableLinkRegistry for read-only access or ModifiableLinkRegistry for full access
 */

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
 * Original expected public links array - maintained for backward compatibility
 * @deprecated Use defaultExpectedLinksRegistry.getAllLinks() for new code
 */
export const expectedPublicLinks = [
  // React routes (handled by client-side routing)
  'standards',
  // Diagram files (still external for now)
  'diagrams/durable-code-flow.html',
  'diagrams/ai-review-sequence.html',
  'diagrams/implementation-plan.html',
];

/**
 * Gets all expected public links from the registry system
 * Use this for new code instead of the deprecated expectedPublicLinks array
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
  const linksToValidate = registry.getAllLinks();
  const results = await validateLinks(linksToValidate, options);
  const missing = results.filter((r) => !r.isValid).map((r) => r.url);

  return {
    allValid: results.every((r) => r.isValid),
    results,
    missing,
  };
}
