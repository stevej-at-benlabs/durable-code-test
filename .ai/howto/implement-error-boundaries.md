# How to Implement Error Boundaries

## Overview
This guide shows how to implement React error boundaries using the 3-tier architecture for robust error handling and recovery.

## Prerequisites
- React application with TypeScript
- Understanding of React component lifecycle
- Access to `src/core/errors/` repository

## Quick Start

### 1. Use MinimalErrorBoundary (Recommended)
```tsx
import { MinimalErrorBoundary } from '../core/errors/MinimalErrorBoundary';

function MyComponent() {
  return (
    <MinimalErrorBoundary>
      {/* Component content that might error */}
      <SomeFeatureComponent />
    </MinimalErrorBoundary>
  );
}
```

### 2. Verify Implementation
```bash
# Test the implementation
make check-page

# Or use direct verification
docker exec durable-code-frontend-dev node /app/scripts/test-rendered-content.js
```

## 3-Tier Implementation Guide

### Tier 1: Root Level (main.tsx)
**Purpose**: Catch any app-wide errors that escape other boundaries

```tsx
// main.tsx
import { MinimalErrorBoundary } from './core/errors/MinimalErrorBoundary';

createRoot(rootElement).render(
  <StrictMode>
    <MinimalErrorBoundary>
      <AppProviders>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </AppProviders>
    </MinimalErrorBoundary>
  </StrictMode>,
);
```

**Testing**:
```bash
make check-page
# Should show: ✅ SUCCESS: App structure looks correct
```

### Tier 2: Route Level (AppShell.tsx)
**Purpose**: Isolate errors to specific pages/routes

```tsx
// AppShell.tsx
import { MinimalErrorBoundary } from '../../core/errors/MinimalErrorBoundary';

export function AppShell(): ReactElement {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <MinimalErrorBoundary>
            <HomePage />
          </MinimalErrorBoundary>
        }
      />
      <Route
        path="/other-page"
        element={
          <MinimalErrorBoundary>
            <OtherPage />
          </MinimalErrorBoundary>
        }
      />
    </Routes>
  );
}
```

**Testing**:
```bash
make check-page
# Test navigation between routes
```

### Tier 3: Component Level (Individual Components)
**Purpose**: Isolate errors in specific features or complex components

```tsx
// HomePage.tsx or any complex component
import { MinimalErrorBoundary } from '../../core/errors/MinimalErrorBoundary';

export default function HomePage(): ReactElement {
  return (
    <div>
      {/* Other content */}

      <MinimalErrorBoundary>
        <Suspense fallback={<LoadingSpinner />}>
          <ComplexFeatureComponent />
        </Suspense>
      </MinimalErrorBoundary>

      {/* More content */}
    </div>
  );
}
```

## Implementation Checklist

### ✅ Before Adding Error Boundaries
- [ ] Read existing component structure
- [ ] Understand component hierarchy
- [ ] Identify error-prone areas (lazy loading, third-party integrations)
- [ ] Test current functionality: `make check-page`

### ✅ During Implementation
- [ ] Start with MinimalErrorBoundary
- [ ] Add one level at a time (root → route → component)
- [ ] Test after each addition: `make check-page`
- [ ] Verify app still functions correctly
- [ ] Check console for any new errors

### ✅ After Implementation
- [ ] Test error boundary with intentional errors
- [ ] Verify recovery mechanisms work
- [ ] Check all routes and features
- [ ] Run full test suite: `make test`
- [ ] Document any special error handling needs

## Testing Error Boundaries

### 1. Verification Tools
```bash
# Basic HTML structure check
make check-page

# Continuous monitoring
make check-page-watch

# Direct content verification
docker exec durable-code-frontend-dev node /app/scripts/test-rendered-content.js

# Advanced verification (requires Playwright)
make check-page-full
```

### 2. Intentional Error Testing
Create a test component to verify error boundaries work:

```tsx
// TestErrorComponent.tsx
function TestErrorComponent({ shouldError }: { shouldError: boolean }) {
  if (shouldError) {
    throw new Error('Test error for boundary verification');
  }
  return <div>No error</div>;
}

// Use in your component
<MinimalErrorBoundary>
  <TestErrorComponent shouldError={false} />
</MinimalErrorBoundary>
```

### 3. Error Boundary Testing Pattern
```tsx
// In your test or development code
import { useState } from 'react';

function ErrorBoundaryTester() {
  const [triggerError, setTriggerError] = useState(false);

  return (
    <div>
      <button onClick={() => setTriggerError(true)}>
        Trigger Error
      </button>

      <MinimalErrorBoundary>
        {triggerError && (() => { throw new Error('Test'); })()}
        <div>Normal content</div>
      </MinimalErrorBoundary>
    </div>
  );
}
```

## Common Patterns

### Pattern 1: Lazy Loading with Error Boundaries
```tsx
const LazyComponent = lazy(() => import('./LazyComponent'));

function ComponentWithLazyLoading() {
  return (
    <MinimalErrorBoundary>
      <Suspense fallback={<LoadingSpinner />}>
        <LazyComponent />
      </Suspense>
    </MinimalErrorBoundary>
  );
}
```

### Pattern 2: Feature Module Error Boundaries
```tsx
// In feature modules
export function FeatureComponent() {
  return (
    <MinimalErrorBoundary>
      <FeatureHeader />
      <FeatureContent />
      <FeatureFooter />
    </MinimalErrorBoundary>
  );
}
```

### Pattern 3: Third-Party Integration Protection
```tsx
function ThirdPartyWrapper() {
  return (
    <MinimalErrorBoundary>
      <ThirdPartyLibraryComponent />
    </MinimalErrorBoundary>
  );
}
```

## Troubleshooting

### Issue: Page Goes Blank After Adding Error Boundary
**Symptoms**: `make check-page` shows empty root div
**Causes**:
- Complex error boundary implementation
- Import errors
- React rendering conflicts

**Solutions**:
1. Use MinimalErrorBoundary instead of ErrorBoundary
2. Check import paths
3. Test incrementally (add one boundary at a time)
4. Remove recently added error boundaries and add back systematically

**Debug Process**:
```bash
# 1. Remove all error boundaries
# 2. Test: make check-page (should work)
# 3. Add root level only
# 4. Test: make check-page
# 5. Add route level
# 6. Test: make check-page
# 7. Add component level
# 8. Test: make check-page
```

### Issue: Error Boundaries Not Catching Errors
**Symptoms**: Errors still crash the app
**Causes**:
- Error boundaries only catch errors in child components
- Async errors not caught by error boundaries
- Event handler errors not caught

**Solutions**:
1. Ensure error boundaries wrap the components that might error
2. Use global error handlers for async errors
3. Add try-catch in event handlers

### Issue: Global Error Handler Breaking App
**Symptoms**: App doesn't start, blank page
**Solution**: Use simplified global error handling in main.tsx:

```tsx
// Simplified global error handling
let errorCount = 0;
let lastErrorTime = 0;
const ERROR_THRESHOLD = 5;
const TIME_WINDOW = 60000;

window.addEventListener('error', (event) => {
  const now = Date.now();
  if (now - lastErrorTime > TIME_WINDOW) errorCount = 0;
  errorCount++;
  lastErrorTime = now;

  if (errorCount >= ERROR_THRESHOLD) {
    console.error('Error storm detected, preventing cascade');
    return;
  }
  console.error('Global error:', event.error);
});
```

## Advanced Usage

### Using Full ErrorBoundary (When Needed)
Only use when you need advanced features like retry/reset:

```tsx
import { ErrorBoundary } from '../core/errors/ErrorBoundary';

function AdvancedComponent() {
  return (
    <ErrorBoundary
      level="component"
      name="AdvancedComponent"
      recoveryOptions={{
        enableAutoRecovery: true,
        maxRetries: 3,
        retryDelay: 1000,
      }}
    >
      <ComplexComponent />
    </ErrorBoundary>
  );
}
```

### Custom Error Fallback
```tsx
function CustomErrorFallback({ error, onReset }: ErrorFallbackProps) {
  return (
    <div style={{ padding: '20px', background: '#fee' }}>
      <h2>Something went wrong</h2>
      <p>{error.message}</p>
      <button onClick={onReset}>Try Again</button>
    </div>
  );
}

<ErrorBoundary fallback={CustomErrorFallback}>
  <Component />
</ErrorBoundary>
```

## Performance Considerations

### Error Boundary Overhead
- MinimalErrorBoundary: ~0ms overhead
- ErrorBoundary: ~1-2ms overhead with recovery features
- Global error handlers: ~0ms overhead

### Best Practices
1. Use MinimalErrorBoundary by default
2. Only add ErrorBoundary when advanced features needed
3. Don't over-wrap components (balance isolation vs. performance)
4. Test performance impact with many error boundaries

## Integration with Testing

### Unit Tests
```tsx
// Test error boundary behavior
import { render } from '@testing-library/react';
import { MinimalErrorBoundary } from '../core/errors/MinimalErrorBoundary';

function ThrowError() {
  throw new Error('Test error');
}

test('error boundary catches and displays error', () => {
  const { getByText } = render(
    <MinimalErrorBoundary>
      <ThrowError />
    </MinimalErrorBoundary>
  );

  expect(getByText('Error occurred')).toBeInTheDocument();
});
```

### E2E Tests
```typescript
// Test error boundary in full application
test('error boundary prevents app crash', async ({ page }) => {
  await page.goto('/');

  // Trigger error
  await page.evaluate(() => {
    throw new Error('Test error');
  });

  // Verify app still responds
  await expect(page.locator('#root')).toBeVisible();
});
```

## Related Documentation
- `.ai/features/error-boundaries.md` - Complete feature documentation
- `.ai/howto/test-page-content.md` - Page verification guide
- `src/core/errors/` - Implementation examples
- `make help` - Available make targets for testing
