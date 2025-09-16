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
 * Categorizes links by type
 */
export function categorizeLinks(urls: string[]): {
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
    if (url.startsWith('http://') || url.startsWith('https://')) {
      absolute.push(url);
      if (url.includes(window.location.hostname)) {
        internal.push(url);
      } else {
        external.push(url);
      }
    } else {
      relative.push(url);
      internal.push(url);
    }
  });

  return { internal, external, relative, absolute };
}

/**
 * Interface for extensible report generators
 */
export interface ReportGenerator {
  generate(
    links: string[],
    results: LinkValidationResult[],
    categories: ReturnType<typeof categorizeLinks>,
  ): any;
}

/**
 * Default report generator implementation
 */
export class DefaultReportGenerator implements ReportGenerator {
  generate(
    links: string[],
    results: LinkValidationResult[],
    categories: ReturnType<typeof categorizeLinks>,
  ) {
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
}

/**
 * Generates a validation report for all links
 * Now supports custom report generators for extensibility
 */
export async function generateLinkReport(
  element: HTMLElement,
  options: LinkValidationOptions & { reportGenerator?: ReportGenerator } = {},
): Promise<any> {
  const links = extractLinksFromElement(element);
  const categories = categorizeLinks(links);
  const results = await validateLinks(links, options);

  // Use custom report generator if provided, otherwise use default
  const generator = options.reportGenerator || new DefaultReportGenerator();
  return generator.generate(links, results, categories);
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
 * Common public links that should exist in the application
 */
export const expectedPublicLinks = [
  // React routes (handled by client-side routing)
  'standards',
  // Diagram files (still external for now)
  'diagrams/durable-code-flow.html',
  'diagrams/ai-review-sequence.html',
  'diagrams/implementation-plan.html',
  // Add more expected public files here as they're created
];

/**
 * Validates that all expected public links exist
 */
export async function validateExpectedLinks(
  options: LinkValidationOptions = {},
): Promise<{
  allValid: boolean;
  results: LinkValidationResult[];
  missing: string[];
}> {
  const results = await validateLinks(expectedPublicLinks, options);
  const missing = results.filter((r) => !r.isValid).map((r) => r.url);

  return {
    allValid: results.every((r) => r.isValid),
    results,
    missing,
  };
}
