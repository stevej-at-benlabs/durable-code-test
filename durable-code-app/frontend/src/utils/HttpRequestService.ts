export interface HttpRequestOptions {
  timeout?: number;
  followRedirects?: boolean;
  checkHeaders?: boolean;
}

export interface HttpResponse {
  ok: boolean;
  status: number;
  responseTime: number;
}

export class UrlNormalizer {
  static normalizeUrl(url: string): string {
    return url.startsWith('http') ? url : `${window.location.origin}/${url}`;
  }
}

export class HttpRequestService {
  async makeRequest(
    url: string,
    options: HttpRequestOptions = {},
  ): Promise<HttpResponse> {
    const { timeout = 5000, followRedirects = true } = options;
    const startTime = Date.now();

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(url, {
        method: 'HEAD',
        signal: controller.signal,
        redirect: followRedirects ? 'follow' : 'manual',
      });

      clearTimeout(timeoutId);
      const responseTime = Date.now() - startTime;

      return {
        ok: response.ok,
        status: response.status,
        responseTime,
      };
    } finally {
      clearTimeout(timeoutId);
    }
  }
}

export interface ValidationResult {
  url: string;
  isValid: boolean;
  status?: number;
  error?: string;
  responseTime: number;
}

export class ValidationResultBuilder {
  static createSuccessResult(url: string, response: HttpResponse): ValidationResult {
    return {
      url,
      isValid: response.ok,
      status: response.status,
      responseTime: response.responseTime,
    };
  }

  static createErrorResult(
    url: string,
    error: unknown,
    responseTime: number,
  ): ValidationResult {
    return {
      url,
      isValid: false,
      error: error instanceof Error ? error.message : 'Unknown error',
      responseTime,
    };
  }
}
