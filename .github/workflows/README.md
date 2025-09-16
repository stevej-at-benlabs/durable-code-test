# Open-Closed Principle (OCP) Violation Checker

This GitHub Action automatically checks pull requests for violations of the SOLID Open-Closed Principle using Claude AI.

## Setup Instructions

### 1. Add Claude API Key to GitHub Secrets

1. Go to your repository's Settings
2. Navigate to "Secrets and variables" > "Actions"
3. Click "New repository secret"
4. Name: `CLAUDE_API_KEY`
5. Value: Your Claude API key (found in the `.env` file)

### 2. How It Works

The action automatically runs when:

- A pull request is opened, synchronized, or reopened
- The PR contains changes to code files (`.py`, `.js`, `.ts`, `.java`, `.cs`, `.go`, `.rb`, `.php`)

### 3. What It Checks

The OCP checker analyzes code changes for common violations including:

- **Modification of existing classes** instead of extending them
- **Switch/if-else chains** that require modification when adding new types
- **Hard-coded dependencies** that violate dependency inversion
- **Direct modification of concrete implementations** instead of using abstractions
- **Lack of extensibility points** in the design

### 4. Severity Levels

- **High**: Critical violations that should be addressed before merging
- **Medium**: Important violations that should be considered
- **Low**: Minor violations or potential improvements

### 5. PR Comments

The action will automatically comment on your PR with:

- A summary of any violations found
- Specific file and line references
- Code snippets showing the violations
- Suggestions for fixing the issues
- Educational information about the Open-Closed Principle

### 6. Build Status

- **Fail**: High severity violations will fail the check
- **Warning**: Medium severity violations will pass but show a warning
- **Pass**: Low severity or no violations will pass the check

## Local Testing

To test the OCP checker locally:

```bash
# Install dependencies
pip install -r .github/scripts/requirements.txt

# Set environment variable
export CLAUDE_API_KEY="your-api-key"

# Run the checker
python .github/scripts/check_ocp_violations.py \
  --base-sha HEAD~1 \
  --head-sha HEAD \
  --pr-number 1 \
  --repo owner/repo
```

## Configuration

The action configuration is in `.github/workflows/ocp-check.yml`. You can modify:

- File patterns to check
- Severity thresholds
- Comment formatting

## Troubleshooting

If the action fails:

1. Check that `CLAUDE_API_KEY` is properly set in GitHub Secrets
2. Verify the API key has sufficient rate limits
3. Check the action logs for specific error messages

## Example Violations

### High Severity Example

```python
# Bad: Modifying existing class for new feature
class OrderProcessor:
    def process(self, order):
        if order.type == "standard":
            # existing code
        elif order.type == "express":  # Added new condition
            # new code
```

### Suggested Fix

```python
# Good: Using abstraction and polymorphism
class OrderProcessor:
    def process(self, order, strategy: OrderStrategy):
        strategy.process(order)

class StandardOrderStrategy(OrderStrategy):
    def process(self, order):
        # standard processing

class ExpressOrderStrategy(OrderStrategy):
    def process(self, order):
        # express processing
```

## Contributing

To improve the OCP checker:

1. Modify `.github/scripts/check_ocp_violations.py`
2. Update the prompt or analysis logic
3. Test locally before committing
4. Submit a PR with your improvements
