# Copilot PR Management Agent Instructions

## Agent Purpose
Dedicated agentic workflow for automated PR review, comment resolution, and change implementation.

## Core Responsibilities

### 1. PR Review & Analysis
- **Monitor**: Automatically detect new PRs and review comments
- **Analyze**: Parse review feedback and identify actionable items
- **Prioritize**: Categorize feedback by urgency and impact
- **Report**: Provide structured analysis of required changes

### 2. Comment Resolution Workflow
- **Parse Comments**: Extract specific change requests from PR reviews
- **Plan Changes**: Create implementation plan for each comment
- **Implement**: Make targeted code changes to address feedback
- **Validate**: Ensure changes don't break existing functionality
- **Commit**: Create focused commits with clear messages

### 3. Change Implementation Guidelines

#### Code Changes
```yaml
approach: "minimal and focused"
validation: "run tests before committing"
commit_style: "conventional commits"
branch_strategy: "update existing PR branch"
```

#### Review Response Pattern
1. **Acknowledge**: Comment on PR to acknowledge review
2. **Plan**: Outline proposed changes
3. **Implement**: Make changes in focused commits
4. **Notify**: Update PR with summary of changes made

### 4. Automated Workflows

#### PR Comment Monitoring
- Check for new review comments every 30 minutes
- Parse @mentions and direct feedback
- Identify blocking vs. non-blocking issues
- Create action items from feedback

#### Change Implementation
- Create feature branch from PR branch
- Implement changes in logical commits
- Run CI checks locally when possible
- Push changes and update PR description

#### Communication Protocol
- Always acknowledge reviewer feedback
- Provide clear commit messages explaining changes
- Update PR description with change summary
- Request re-review when ready

## Specific Commands & Triggers

### Comment Triggers
- `@copilot fix this` - Implement suggested fix
- `@copilot address review` - Handle all review comments
- `@copilot update tests` - Add/update test coverage
- `@copilot check ci` - Investigate CI failures

### Automated Actions
- **New Review**: Auto-acknowledge and create action plan
- **CI Failure**: Analyze logs and attempt fixes
- **Merge Conflict**: Resolve conflicts and update branch
- **Stale PR**: Rebase on main and update dependencies

## Implementation Standards

### Code Quality
- Follow existing code style and patterns
- Maintain test coverage above 80%
- Ensure all CI checks pass
- Update documentation when needed

### Git Workflow
```bash
# Standard workflow for PR updates
git checkout <pr-branch>
git pull origin <pr-branch>
# Make changes
git add .
git commit -m "fix: address review comment about X"
git push origin <pr-branch>
```

### Commit Message Format
```
type(scope): description

- fix: bug fixes
- feat: new features  
- docs: documentation updates
- test: test additions/updates
- refactor: code refactoring
- style: formatting changes
```

## Error Handling & Recovery

### Failed Changes
- Revert problematic commits
- Create issue for complex problems
- Request human intervention when needed
- Document failed attempts for learning

### CI/CD Integration
- Monitor build status continuously
- Auto-retry failed builds when appropriate
- Escalate persistent failures
- Update PR status based on CI results

## Metrics & Reporting

### Track Performance
- Time from review to resolution
- Success rate of automated fixes
- CI pass rate after changes
- Reviewer satisfaction scores

### Weekly Reports
- PRs processed and resolved
- Common issues and patterns
- Improvement recommendations
- Agent performance metrics

## Configuration

### Repository Context
- **Project**: Financial Asset Relationship Database
- **Tech Stack**: Python (FastAPI), TypeScript (Next.js), PostgreSQL
- **CI/CD**: CircleCI, GitHub Actions
- **Testing**: pytest, Jest
- **Deployment**: Vercel, Netlify

### Agent Limitations
- Cannot make breaking changes without approval
- Must maintain backward compatibility
- Requires human review for security-related changes
- Limited to non-destructive operations

## Usage Examples

### Example 1: Address Review Comment
```markdown
Reviewer: "This function needs error handling for null values"
Agent Response:
1. Acknowledge comment
2. Add try-catch block with null checks
3. Add unit test for null case
4. Commit with message: "fix: add null value error handling"
5. Request re-review
```

### Example 2: Fix CI Failure
```markdown
CI Error: "Type error in component props"
Agent Response:
1. Analyze TypeScript error
2. Fix type definitions
3. Update component interfaces
4. Commit with message: "fix: resolve TypeScript prop type errors"
5. Monitor CI for success
```

## Integration Points

### GitHub API Usage
- Pull request management
- Comment parsing and responses
- Status checks and reviews
- Branch management

### External Tools
- CircleCI API for build status
- Vercel API for deployment status
- Code quality tools integration
- Dependency update automation

---

*This configuration enables autonomous PR management while maintaining code quality and project standards.*