/**
 * Purpose: Service for generating link validation reports
 * Scope: Report generation, formatting, and summary creation
 * Created: 2025-09-16
 * Updated: 2025-09-16
 * Author: Development Team
 * Version: 1.0
 */

import type { LinkValidationResult } from './LinkValidationService';

/**
 * Interface for building different types of reports
 */
export interface LinkReportSummary {
  summary: {
    total: number;
    valid: number;
    broken: number;
  };
  results: LinkValidationResult[];
}

/**
 * Detailed report with additional metrics
 */
export interface DetailedLinkReport extends LinkReportSummary {
  averageResponseTime: number;
  statusCodeBreakdown: Record<number, number>;
  errorTypes: Record<string, number>;
  slowestLinks: Array<{ url: string; responseTime: number }>;
}

/**
 * Report builder interface for extensible report generation
 */
export interface ReportBuilder {
  buildSummary(results: LinkValidationResult[]): LinkReportSummary;
}

/**
 * Default summary report builder
 */
export class SummaryReportBuilder implements ReportBuilder {
  buildSummary(results: LinkValidationResult[]): LinkReportSummary {
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
 * Detailed report builder with additional metrics
 */
export class DetailedReportBuilder implements ReportBuilder {
  buildSummary(results: LinkValidationResult[]): DetailedLinkReport {
    const basic = new SummaryReportBuilder().buildSummary(results);

    // Calculate average response time
    const validResults = results.filter((r) => r.isValid);
    const totalResponseTime = validResults.reduce((sum, r) => sum + r.responseTime, 0);
    const averageResponseTime =
      validResults.length > 0 ? totalResponseTime / validResults.length : 0;

    // Status code breakdown
    const statusCodeBreakdown: Record<number, number> = {};
    validResults.forEach((r) => {
      if (r.statusCode) {
        statusCodeBreakdown[r.statusCode] =
          (statusCodeBreakdown[r.statusCode] || 0) + 1;
      }
    });

    // Error type breakdown
    const errorTypes: Record<string, number> = {};
    results
      .filter((r) => !r.isValid)
      .forEach((r) => {
        const errorType = r.error || 'Unknown';
        errorTypes[errorType] = (errorTypes[errorType] || 0) + 1;
      });

    // Find slowest links
    const slowestLinks = [...validResults]
      .sort((a, b) => b.responseTime - a.responseTime)
      .slice(0, 5)
      .map((r) => ({ url: r.url, responseTime: r.responseTime }));

    return {
      ...basic,
      averageResponseTime,
      statusCodeBreakdown,
      errorTypes,
      slowestLinks,
    };
  }
}

/**
 * CSV report builder for exporting results
 */
export class CsvReportBuilder implements ReportBuilder {
  buildSummary(results: LinkValidationResult[]): LinkReportSummary & { csv: string } {
    const basic = new SummaryReportBuilder().buildSummary(results);

    // Generate CSV content
    const headers = ['URL', 'Valid', 'Status Code', 'Response Time (ms)', 'Error'];
    const rows = results.map((r) => [
      r.url,
      r.isValid ? 'Yes' : 'No',
      r.statusCode?.toString() || '',
      r.responseTime.toString(),
      r.error || '',
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map((row) => row.map((cell) => `"${cell}"`).join(',')),
    ].join('\n');

    return {
      ...basic,
      csv: csvContent,
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

  createReport(results: LinkValidationResult[]): LinkReportSummary {
    return this.builder.buildSummary(results);
  }

  /**
   * Create different types of reports
   */
  createSummaryReport(results: LinkValidationResult[]): LinkReportSummary {
    const originalBuilder = this.builder;
    this.builder = new SummaryReportBuilder();
    const report = this.createReport(results);
    this.builder = originalBuilder;
    return report;
  }

  createDetailedReport(results: LinkValidationResult[]): DetailedLinkReport {
    const originalBuilder = this.builder;
    this.builder = new DetailedReportBuilder();
    const report = this.createReport(results) as DetailedLinkReport;
    this.builder = originalBuilder;
    return report;
  }

  createCsvReport(
    results: LinkValidationResult[],
  ): LinkReportSummary & { csv: string } {
    const originalBuilder = this.builder;
    this.builder = new CsvReportBuilder();
    const report = this.createReport(results) as LinkReportSummary & { csv: string };
    this.builder = originalBuilder;
    return report;
  }

  /**
   * Generate report with performance metrics
   */
  generatePerformanceReport(results: LinkValidationResult[]): {
    fast: LinkValidationResult[]; // < 200ms
    medium: LinkValidationResult[]; // 200-1000ms
    slow: LinkValidationResult[]; // > 1000ms
    averageResponseTime: number;
  } {
    const fast = results.filter((r) => r.isValid && r.responseTime < 200);
    const medium = results.filter(
      (r) => r.isValid && r.responseTime >= 200 && r.responseTime < 1000,
    );
    const slow = results.filter((r) => r.isValid && r.responseTime >= 1000);

    const validResults = results.filter((r) => r.isValid);
    const totalResponseTime = validResults.reduce((sum, r) => sum + r.responseTime, 0);
    const averageResponseTime =
      validResults.length > 0 ? totalResponseTime / validResults.length : 0;

    return {
      fast,
      medium,
      slow,
      averageResponseTime,
    };
  }
}

// Export standalone function for backward compatibility
export function createLinkReportSummary(
  results: LinkValidationResult[],
): LinkReportSummary {
  const service = new LinkReportService();
  return service.createReport(results);
}
