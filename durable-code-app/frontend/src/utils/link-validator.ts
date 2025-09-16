/**
 * Purpose: Utility functions for validating links and external resources
 * Scope: Link checking, resource validation, and broken link detection
 * Created: 2025-09-12
 * Updated: 2025-09-12
 * Author: Development Team
 * Version: 1.0
 */

export interface LinkValidationResult {
  url: string;
  isValid: boolean;
  status?: number;
  error?: string;
  responseTime?: number;
}

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
  const { timeout = 5000, followRedirects = true } = options;
  const startTime = Date.now();

  try {
    // Handle relative URLs
    const fullUrl = url.startsWith('http') ? url : `${window.location.origin}/${url}`;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    const response = await fetch(fullUrl, {
      method: 'HEAD', // Use HEAD to avoid downloading content
      signal: controller.signal,
      redirect: followRedirects ? 'follow' : 'manual',
    });

    clearTimeout(timeoutId);
    const responseTime = Date.now() - startTime;

    return {
      url,
      isValid: response.ok,
      status: response.status,
      responseTime,
    };
  } catch (error) {
    const responseTime = Date.now() - startTime;

    return {
      url,
      isValid: false,
      error: error instanceof Error ? error.message : 'Unknown error',
      responseTime,
    };
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
  const links: string[] = [];

  // Get all anchor tags
  const anchors = element.querySelectorAll('a[href]');
  anchors.forEach((anchor) => {
    const href = anchor.getAttribute('href');
    if (href && !href.startsWith('mailto:') && !href.startsWith('tel:')) {
      links.push(href);
    }
  });

  // Get all img tags
  const images = element.querySelectorAll('img[src]');
  images.forEach((img) => {
    const src = img.getAttribute('src');
    if (src) {
      links.push(src);
    }
  });

  // Get all script tags with src
  const scripts = element.querySelectorAll('script[src]');
  scripts.forEach((script) => {
    const src = script.getAttribute('src');
    if (src) {
      links.push(src);
    }
  });

  // Get all link tags with href (CSS, etc.)
  const linkTags = element.querySelectorAll('link[href]');
  linkTags.forEach((link) => {
    const href = link.getAttribute('href');
    if (href) {
      links.push(href);
    }
  });

  return [...new Set(links)]; // Remove duplicates
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
 * Creates a link report summary from validation results
 */
export function createLinkReportSummary(results: LinkValidationResult[]) {
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

/**
 * Link registry interface for managing expected links
 */
export interface LinkRegistry {
  getLinks(): string[];
  addLink(link: string): void;
  removeLink(link: string): void;
}

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
 * Backward compatibility - gets all expected public links
 */
export const expectedPublicLinks = defaultExpectedLinksRegistry.getAllLinks();

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
