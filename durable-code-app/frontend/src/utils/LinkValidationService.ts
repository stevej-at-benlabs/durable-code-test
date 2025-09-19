/**
 * Purpose: Service for HTTP link validation functionality
 * Scope: HTTP requests, link validation, and result handling
 * Created: 2025-09-16
 * Updated: 2025-09-16
 * Author: Development Team
 * Version: 1.0
 */

import {
  createErrorResult,
  createSuccessResult,
  HttpRequestService,
  normalizeUrl,
} from './HttpRequestService';
import type { ValidationResult } from './HttpRequestService';

export type LinkValidationResult = ValidationResult;

export interface LinkValidationOptions {
  timeout?: number;
  followRedirects?: boolean;
  checkHeaders?: boolean;
}

/**
 * Service for validating HTTP/HTTPS links
 */
export class LinkValidationService {
  private httpService: HttpRequestService;

  constructor(httpService?: HttpRequestService) {
    this.httpService = httpService || new HttpRequestService();
  }

  /**
   * Validates a single link by making an HTTP request
   */
  async validateLink(
    url: string,
    options: LinkValidationOptions = {},
  ): Promise<LinkValidationResult> {
    const startTime = Date.now();

    try {
      const fullUrl = normalizeUrl(url);
      const response = await this.httpService.makeRequest(fullUrl, options);

      return createSuccessResult(url, response);
    } catch (error) {
      const responseTime = Date.now() - startTime;
      return createErrorResult(url, error, responseTime);
    }
  }

  /**
   * Validates multiple links concurrently
   */
  async validateLinks(
    urls: string[],
    options: LinkValidationOptions = {},
  ): Promise<LinkValidationResult[]> {
    const validationPromises = urls.map((url) => this.validateLink(url, options));
    return Promise.all(validationPromises);
  }
}

// Export standalone functions for backward compatibility
export async function validateLink(
  url: string,
  options: LinkValidationOptions = {},
): Promise<LinkValidationResult> {
  const service = new LinkValidationService();
  return service.validateLink(url, options);
}

export async function validateLinks(
  urls: string[],
  options: LinkValidationOptions = {},
): Promise<LinkValidationResult[]> {
  const service = new LinkValidationService();
  return service.validateLinks(urls, options);
}
