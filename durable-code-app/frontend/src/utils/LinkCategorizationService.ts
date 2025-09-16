/**
 * Purpose: Service for categorizing and classifying links
 * Scope: Link categorization strategies and classification logic
 * Created: 2025-09-16
 * Updated: 2025-09-16
 * Author: Development Team
 * Version: 1.0
 */

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
 * Hash link categorizer for anchors
 */
export class HashLinkCategorizer implements LinkCategorizer {
  categorize(url: string): string[] {
    if (url.startsWith('#')) {
      return ['anchor', 'internal'];
    }
    return [];
  }
}

/**
 * Protocol-specific categorizer (mailto, tel, etc.)
 */
export class ProtocolLinkCategorizer implements LinkCategorizer {
  private protocols = ['mailto:', 'tel:', 'ftp:', 'file:'];

  categorize(url: string): string[] {
    for (const protocol of this.protocols) {
      if (url.startsWith(protocol)) {
        return ['protocol', protocol.slice(0, -1)]; // Remove colon
      }
    }
    return [];
  }
}

export interface CategorizedLinks {
  internal: string[];
  external: string[];
  relative: string[];
  absolute: string[];
  anchor?: string[];
  protocol?: string[];
}

/**
 * Link categorization service that supports multiple categorizers
 */
export class LinkCategorizationService {
  private categorizers: LinkCategorizer[] = [];

  constructor(categorizers?: LinkCategorizer[]) {
    this.categorizers = categorizers || [
      new HttpLinkCategorizer(),
      new RelativeLinkCategorizer(),
      new HashLinkCategorizer(),
      new ProtocolLinkCategorizer(),
    ];
  }

  addCategorizer(categorizer: LinkCategorizer): void {
    this.categorizers.push(categorizer);
  }

  removeCategorizer(categorizer: LinkCategorizer): void {
    this.categorizers = this.categorizers.filter((c) => c !== categorizer);
  }

  /**
   * Categorize a single URL
   */
  categorizeUrl(url: string): string[] {
    const allCategories = new Set<string>();

    this.categorizers.forEach((categorizer) => {
      const categories = categorizer.categorize(url);
      categories.forEach((category) => allCategories.add(category));
    });

    return Array.from(allCategories);
  }

  /**
   * Categorize multiple URLs
   */
  categorizeLinks(urls: string[]): CategorizedLinks {
    const result: CategorizedLinks = {
      internal: [],
      external: [],
      relative: [],
      absolute: [],
      anchor: [],
      protocol: [],
    };

    urls.forEach((url) => {
      const categories = this.categorizeUrl(url);

      // Sort URLs into appropriate arrays based on categories
      if (categories.includes('internal')) result.internal.push(url);
      if (categories.includes('external')) result.external.push(url);
      if (categories.includes('relative')) result.relative.push(url);
      if (categories.includes('absolute')) result.absolute.push(url);
      if (categories.includes('anchor') && result.anchor) result.anchor.push(url);
      if (categories.includes('protocol') && result.protocol) result.protocol.push(url);
    });

    return result;
  }
}

// Export standalone function for backward compatibility
export function categorizeLinks(urls: string[]): {
  internal: string[];
  external: string[];
  relative: string[];
  absolute: string[];
} {
  const service = new LinkCategorizationService([
    new HttpLinkCategorizer(),
    new RelativeLinkCategorizer(),
  ]);
  const categorized = service.categorizeLinks(urls);

  return {
    internal: categorized.internal,
    external: categorized.external,
    relative: categorized.relative,
    absolute: categorized.absolute,
  };
}
