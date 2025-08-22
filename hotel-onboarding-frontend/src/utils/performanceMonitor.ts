/**
 * Performance Monitoring Utility
 * 
 * Tracks and reports Core Web Vitals and custom metrics
 * for the job application form.
 * 
 * Metrics tracked:
 * - First Contentful Paint (FCP)
 * - Largest Contentful Paint (LCP)
 * - First Input Delay (FID)
 * - Cumulative Layout Shift (CLS)
 * - Time to Interactive (TTI)
 * - Custom form metrics
 */

interface PerformanceMetrics {
  FCP?: number;
  LCP?: number;
  FID?: number;
  CLS?: number;
  TTI?: number;
  formLoadTime?: number;
  stepTransitionTime?: number;
  bundleSize?: number;
}

class PerformanceMonitor {
  private metrics: PerformanceMetrics = {};
  private observers: Map<string, PerformanceObserver> = new Map();
  
  constructor() {
    if (typeof window !== 'undefined' && 'PerformanceObserver' in window) {
      this.initializeObservers();
    }
  }
  
  private initializeObservers() {
    // First Contentful Paint
    try {
      const fcpObserver = new PerformanceObserver((entryList) => {
        for (const entry of entryList.getEntriesByName('first-contentful-paint')) {
          this.metrics.FCP = entry.startTime;
          this.reportMetric('FCP', entry.startTime);
        }
      });
      fcpObserver.observe({ type: 'paint', buffered: true });
      this.observers.set('fcp', fcpObserver);
    } catch (e) {
      console.warn('FCP observer not supported');
    }
    
    // Largest Contentful Paint
    try {
      const lcpObserver = new PerformanceObserver((entryList) => {
        const entries = entryList.getEntries();
        const lastEntry = entries[entries.length - 1];
        this.metrics.LCP = lastEntry.startTime;
        this.reportMetric('LCP', lastEntry.startTime);
      });
      lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true });
      this.observers.set('lcp', lcpObserver);
    } catch (e) {
      console.warn('LCP observer not supported');
    }
    
    // First Input Delay
    try {
      const fidObserver = new PerformanceObserver((entryList) => {
        for (const entry of entryList.getEntries()) {
          const fidEntry = entry as any;
          this.metrics.FID = fidEntry.processingStart - fidEntry.startTime;
          this.reportMetric('FID', this.metrics.FID);
        }
      });
      fidObserver.observe({ type: 'first-input', buffered: true });
      this.observers.set('fid', fidObserver);
    } catch (e) {
      console.warn('FID observer not supported');
    }
    
    // Cumulative Layout Shift
    try {
      let clsValue = 0;
      const clsObserver = new PerformanceObserver((entryList) => {
        for (const entry of entryList.getEntries()) {
          const layoutShift = entry as any;
          if (!layoutShift.hadRecentInput) {
            clsValue += layoutShift.value;
            this.metrics.CLS = clsValue;
          }
        }
      });
      clsObserver.observe({ type: 'layout-shift', buffered: true });
      this.observers.set('cls', clsObserver);
    } catch (e) {
      console.warn('CLS observer not supported');
    }
  }
  
  // Track custom form metrics
  public trackFormLoad(startTime: number) {
    const loadTime = performance.now() - startTime;
    this.metrics.formLoadTime = loadTime;
    this.reportMetric('Form Load Time', loadTime);
  }
  
  public trackStepTransition(startTime: number) {
    const transitionTime = performance.now() - startTime;
    this.metrics.stepTransitionTime = transitionTime;
    this.reportMetric('Step Transition Time', transitionTime);
  }
  
  // Report metrics
  private reportMetric(name: string, value: number) {
    // In production, send to analytics service
    if (process.env.NODE_ENV === 'development') {
      console.log(`[Performance] ${name}: ${value.toFixed(2)}ms`);
    }
    
    // Check against thresholds
    this.checkThresholds(name, value);
  }
  
  private checkThresholds(name: string, value: number) {
    const thresholds: Record<string, { good: number; needsImprovement: number }> = {
      FCP: { good: 1800, needsImprovement: 3000 },
      LCP: { good: 2500, needsImprovement: 4000 },
      FID: { good: 100, needsImprovement: 300 },
      CLS: { good: 0.1, needsImprovement: 0.25 },
      'Form Load Time': { good: 1500, needsImprovement: 3000 },
      'Step Transition Time': { good: 300, needsImprovement: 500 }
    };
    
    const threshold = thresholds[name];
    if (threshold) {
      if (value <= threshold.good) {
        console.log(`✅ ${name} is GOOD`);
      } else if (value <= threshold.needsImprovement) {
        console.log(`⚠️ ${name} NEEDS IMPROVEMENT`);
      } else {
        console.log(`❌ ${name} is POOR`);
      }
    }
  }
  
  // Get all metrics
  public getMetrics(): PerformanceMetrics {
    return { ...this.metrics };
  }
  
  // Generate performance report
  public generateReport(): string {
    const report: string[] = [
      '=== Performance Report ===',
      `First Contentful Paint: ${this.metrics.FCP?.toFixed(2) || 'N/A'}ms`,
      `Largest Contentful Paint: ${this.metrics.LCP?.toFixed(2) || 'N/A'}ms`,
      `First Input Delay: ${this.metrics.FID?.toFixed(2) || 'N/A'}ms`,
      `Cumulative Layout Shift: ${this.metrics.CLS?.toFixed(4) || 'N/A'}`,
      `Form Load Time: ${this.metrics.formLoadTime?.toFixed(2) || 'N/A'}ms`,
      `Step Transition Time: ${this.metrics.stepTransitionTime?.toFixed(2) || 'N/A'}ms`
    ];
    
    return report.join('\n');
  }
  
  // Cleanup observers
  public disconnect() {
    this.observers.forEach((observer) => observer.disconnect());
    this.observers.clear();
  }
}

// Export singleton instance
export const performanceMonitor = new PerformanceMonitor();

// Export utility functions
export const measurePerformance = (name: string, fn: () => void) => {
  const startTime = performance.now();
  fn();
  const endTime = performance.now();
  const duration = endTime - startTime;
  console.log(`[Performance] ${name}: ${duration.toFixed(2)}ms`);
  return duration;
};

export const measureAsyncPerformance = async (name: string, fn: () => Promise<void>) => {
  const startTime = performance.now();
  await fn();
  const endTime = performance.now();
  const duration = endTime - startTime;
  console.log(`[Performance] ${name}: ${duration.toFixed(2)}ms`);
  return duration;
};

export default performanceMonitor;