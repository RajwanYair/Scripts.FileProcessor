# .github Directory

This directory contains GitHub-specific configuration and community health files following standard open-source conventions.

## Structure

```
.github/
├── ISSUE_TEMPLATE/              # Issue forms (bug report, feature request, etc.)
│   ├── bug_report.yml
│   ├── feature_request.yml
│   ├── documentation.yml
│   ├── plugin_request.yml
│   ├── performance_issue.md
│   └── config.yml
├── workflows/                   # GitHub Actions CI/CD pipelines
│   ├── ci-cd.yml                # Main CI pipeline (lint → test → build → deploy)
│   ├── codeql.yml               # CodeQL security analysis (SAST)
│   ├── release.yml              # Triggered on version tags — publishes releases
│   └── labeler.yml              # Auto-labels PRs by changed files
├── instructions/                # Copilot coding guidelines (applyTo per file type)
│   ├── python.instructions.md
│   ├── testing.instructions.md
│   └── cicd.instructions.md
├── prompts/                     # Reusable Copilot prompt files
│   ├── code-review.prompt.md
│   ├── write-tests.prompt.md
│   ├── fix-quality.prompt.md
│   └── create-project.prompt.md
├── pull_request_template/       # PR checklist template
│   └── pull_request_template.md
├── CODEOWNERS                   # Auto-assign reviewers by changed path
├── copilot-instructions.md      # Project-level Copilot instructions
├── dependabot.yml               # Automated dependency update schedule
├── labeler.yml                  # Label-to-path mapping for the labeler workflow
├── pull_request_template.md     # Default PR template
└── README.md                    # This file
```

## Community Health Files

The root-level files (`README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `CHANGELOG.md`, `ROADMAP.md`) are the canonical GitHub community health files and live at the repository root per GitHub conventions.

## Workflows Overview

| Workflow | Trigger | Purpose |
|---|---|---|
| `ci-cd.yml` | push/PR to `main`/`develop` | Lint → Test → Build → Deploy |
| `codeql.yml` | push/PR + weekly schedule | SAST security scanning |
| `release.yml` | tag push `v*.*.*` | Build, publish, create release |
| `labeler.yml` | PR open/sync | Auto-label by changed files |

### Creating Issues

1. Navigate to "Issues" → "New Issue"
2. Select appropriate template (Bug Report or Feature Request)
3. Fill in all required fields
4. Submit with auto-generated labels

### Submitting Pull Requests

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes and commit
3. Push branch: `git push origin feature/my-feature`
4. Open PR - template auto-populates
5. Complete all checklist items
6. Request review

### Running Workflows

Workflows trigger automatically on:

- Push to `main`/`develop`
- Pull request creation/update
- Release publication

Manual trigger:

1. Go to "Actions" tab
2. Select workflow
3. Click "Run workflow"

## Best Practices

### For Maintainers

1. **Review Templates**: Update templates as project evolves
2. **Workflow Maintenance**: Keep actions/dependencies current
3. **Label Management**: Ensure auto-labels are configured
4. **Branch Protection**: Require workflow success before merge
5. **Secrets Rotation**: Regularly rotate API keys/tokens

### For Contributors

1. **Use Templates**: Always use issue/PR templates
2. **Complete Checklists**: Check all applicable boxes
3. **Link Issues**: Reference related issues in PRs
4. **Test Locally**: Run CI checks before pushing
5. **Update Docs**: Keep documentation in sync with changes

## Configuration

### Required Repository Settings

**Branch Protection (main)**:

- ✅ Require pull request reviews (1 approval)
- ✅ Require status checks to pass
- ✅ Require branches to be up to date
- ✅ Require linear history
- ✅ Include administrators

**Actions**:

- ✅ Allow all actions and reusable workflows
- ✅ Read and write permissions
- ✅ Allow GitHub Actions to create PRs

**Security**:

- ✅ Private vulnerability reporting
- ✅ Dependabot alerts
- ✅ Code scanning alerts

### Required Secrets

Add in Settings → Secrets → Actions:

```
DOCKER_USERNAME      # Docker Hub username
DOCKER_PASSWORD      # Docker Hub token
PYPI_API_TOKEN       # PyPI publishing token
SAFETY_API_KEY       # Safety vulnerability scanning API key
```

## Customization

### Adding New Issue Types

1. Create new YAML file in `ISSUE_TEMPLATE/`
2. Follow GitHub issue form schema
3. Add to `config.yml` if needed
4. Update this README

### Modifying Workflows

1. Edit workflow YAML in `workflows/`
2. Test with `act` or draft PR
3. Update workflow README
4. Document any new secrets needed

### Changing PR Template

1. Edit `PULL_REQUEST_TEMPLATE/pull_request_template.md`
2. Ensure checklist items are relevant
3. Update any linked documentation

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Issue Templates Guide](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests)
- [Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)
- [GitHub Community Standards](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions)

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for general contribution guidelines.
