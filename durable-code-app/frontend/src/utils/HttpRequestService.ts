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

export interface RequestStrategy {
  makeRequest(url: string, options: HttpRequestOptions): Promise<HttpResponse>;
}

export class FetchRequestStrategy implements RequestStrategy {
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

export function normalizeUrl(url: string): string {
  return url.startsWith('http') ? url : `${window.location.origin}/${url}`;
}

export class HttpRequestService {
  private strategy: RequestStrategy;

  constructor(strategy?: RequestStrategy) {
    this.strategy = strategy || new FetchRequestStrategy();
  }

  setStrategy(strategy: RequestStrategy): void {
    this.strategy = strategy;
  }

  async makeRequest(
    url: string,
    options: HttpRequestOptions = {},
  ): Promise<HttpResponse> {
    return this.strategy.makeRequest(url, options);
  }
}

export interface ValidationResult {
  url: string;
  isValid: boolean;
  status?: number;
  error?: string;
  responseTime: number;
}

export function createSuccessResult(
  url: string,
  response: HttpResponse,
): ValidationResult {
  return {
    url,
    isValid: response.ok,
    status: response.status,
    responseTime: response.responseTime,
  };
}

export function createErrorResult(
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
