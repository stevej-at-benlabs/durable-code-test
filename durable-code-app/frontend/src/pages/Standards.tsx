/**
 * Standards Page - Development Standards and Best Practices
 * Integrated React component to replace external HTML file
 */
import { useNavigate, useSearchParams } from 'react-router-dom';
import './Standards.css';

function Standards() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const returnTab = searchParams.get('return') || 'Building';

  const handleBackClick = () => {
    navigate(`/#${returnTab}`);
  };

  return (
    <div className="standards-page">
      <div className="breadcrumb">
        <button onClick={handleBackClick} className="breadcrumb-link">
          ← Back to {returnTab}
        </button>
        <span className="breadcrumb-separator">/</span>
        <span className="breadcrumb-current">Development Standards</span>
      </div>

      <div className="container">
        <header className="page-header">
          <h1 className="page-title">Development Standards Guide</h1>
          <p className="page-subtitle">
            Comprehensive guidelines for AI-assisted development and code quality
          </p>
        </header>

        <main className="content">
          <section>
            <h2 className="section-title">Code Quality Standards</h2>

            <div className="subsection">
              <h3 className="subsection-title">Naming Conventions</h3>
              <ul className="standards-list">
                <li>
                  <strong>Variables:</strong> Use descriptive camelCase names (e.g.,{' '}
                  <code>userAccountBalance</code>)
                </li>
                <li>
                  <strong>Functions:</strong> Use verbs that describe actions (e.g.,{' '}
                  <code>calculateTotal</code>, <code>validateInput</code>)
                </li>
                <li>
                  <strong>Classes:</strong> Use PascalCase nouns (e.g.,{' '}
                  <code>UserAccount</code>, <code>PaymentProcessor</code>)
                </li>
                <li>
                  <strong>Constants:</strong> Use SCREAMING_SNAKE_CASE (e.g.,{' '}
                  <code>MAX_RETRY_ATTEMPTS</code>)
                </li>
              </ul>
            </div>

            <div className="subsection">
              <h3 className="subsection-title">Code Structure</h3>
              <ul className="standards-list">
                <li>Maximum function length: 50 lines</li>
                <li>Maximum file length: 500 lines</li>
                <li>Use TypeScript for all new code</li>
                <li>Include JSDoc comments for public APIs</li>
                <li>Follow SOLID principles</li>
              </ul>
            </div>
          </section>

          <section>
            <h2 className="section-title">Testing Standards</h2>

            <div className="subsection">
              <h3 className="subsection-title">Unit Testing</h3>
              <ul className="standards-list">
                <li>Minimum 80% code coverage</li>
                <li>
                  Test file naming: <code>ComponentName.test.tsx</code>
                </li>
                <li>Use descriptive test names that explain the scenario</li>
                <li>Follow Arrange-Act-Assert pattern</li>
              </ul>
            </div>

            <div className="code-block">
              <pre>{`// Example test structure
describe('UserAccount', () => {
  it('should calculate balance correctly when deposits exceed withdrawals', () => {
    // Arrange
    const account = new UserAccount(100);

    // Act
    account.deposit(50);
    account.withdraw(25);

    // Assert
    expect(account.getBalance()).toBe(125);
  });
});`}</pre>
            </div>
          </section>

          <section>
            <h2 className="section-title">AI Development Guidelines</h2>

            <div className="subsection">
              <h3 className="subsection-title">Context Management</h3>
              <ul className="standards-list">
                <li>Maintain comprehensive README files</li>
                <li>Document business logic and domain knowledge</li>
                <li>Include examples of good and bad patterns</li>
                <li>Keep .ai folder updated with project context</li>
              </ul>
            </div>

            <div className="subsection">
              <h3 className="subsection-title">Code Generation Standards</h3>
              <ul className="standards-list">
                <li>Always include error handling</li>
                <li>Add proper TypeScript types</li>
                <li>Include unit tests with generated code</li>
                <li>Follow existing project patterns</li>
              </ul>
            </div>
          </section>

          <section>
            <h2 className="section-title">Quality Assurance</h2>

            <div className="subsection">
              <h3 className="subsection-title">Automated Checks</h3>
              <ul className="standards-list">
                <li>ESLint for code style</li>
                <li>Prettier for formatting</li>
                <li>TypeScript for type safety</li>
                <li>Custom linters for project-specific rules</li>
              </ul>
            </div>

            <div className="subsection">
              <h3 className="subsection-title">CI/CD Requirements</h3>
              <ul className="standards-list">
                <li>All tests must pass</li>
                <li>No linting errors</li>
                <li>Type checking passes</li>
                <li>Build succeeds</li>
                <li>Security scans pass</li>
              </ul>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}

export default Standards;
