export class AnchorLinkExtractor {
  extract(element: HTMLElement): string[] {
    const links: string[] = [];
    const anchors = element.querySelectorAll('a[href]');

    anchors.forEach((anchor) => {
      const href = anchor.getAttribute('href');
      if (href && !href.startsWith('mailto:') && !href.startsWith('tel:')) {
        links.push(href);
      }
    });

    return links;
  }
}

export class ImageLinkExtractor {
  extract(element: HTMLElement): string[] {
    const links: string[] = [];
    const images = element.querySelectorAll('img[src]');

    images.forEach((img) => {
      const src = img.getAttribute('src');
      if (src) {
        links.push(src);
      }
    });

    return links;
  }
}

export class ScriptLinkExtractor {
  extract(element: HTMLElement): string[] {
    const links: string[] = [];
    const scripts = element.querySelectorAll('script[src]');

    scripts.forEach((script) => {
      const src = script.getAttribute('src');
      if (src) {
        links.push(src);
      }
    });

    return links;
  }
}

export class StylesheetLinkExtractor {
  extract(element: HTMLElement): string[] {
    const links: string[] = [];
    const linkTags = element.querySelectorAll('link[href]');

    linkTags.forEach((link) => {
      const href = link.getAttribute('href');
      if (href) {
        links.push(href);
      }
    });

    return links;
  }
}

export interface LinkExtractor {
  extract(element: HTMLElement): string[];
}

export class CompositeLinkExtractor {
  private extractors: LinkExtractor[] = [];

  constructor(extractors: LinkExtractor[] = []) {
    this.extractors =
      extractors.length > 0
        ? extractors
        : [
            new AnchorLinkExtractor(),
            new ImageLinkExtractor(),
            new ScriptLinkExtractor(),
            new StylesheetLinkExtractor(),
          ];
  }

  addExtractor(extractor: LinkExtractor): void {
    this.extractors.push(extractor);
  }

  extractAllLinks(element: HTMLElement): string[] {
    const allLinks: string[] = [];

    this.extractors.forEach((extractor) => {
      const links = extractor.extract(element);
      allLinks.push(...links);
    });

    // Remove duplicates
    return [...new Set(allLinks)];
  }
}
