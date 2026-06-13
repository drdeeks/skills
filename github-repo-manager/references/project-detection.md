# Project Type Detection

Reference guide for detecting project types from repository contents.

## Detection Methods

### File-Based Detection

The primary method for detecting project types is examining the presence of characteristic files in the repository root.

#### Programming Language Indicators

| Language | Indicator Files |
|----------|-----------------|
| **Python** | requirements.txt, setup.py, pyproject.toml, Pipfile, tox.ini, .python-version |
| **Node.js** | package.json, yarn.lock, pnpm-lock.yaml, npm-shrinkwrap.json, .nvmrc |
| **Rust** | Cargo.toml, Cargo.lock, rustfmt.toml |
| **Go** | go.mod, go.sum |
| **Java** | pom.xml, build.gradle, build.gradle.kts, settings.gradle |
| **C#** | *.csproj, *.vbproj, *.sln, packages.config |
| **PHP** | composer.json, composer.lock |
| **Ruby** | Gemfile, Gemfile.lock, .ruby-version |
| **Swift** | Package.swift, *.xcodeproj |
| **Elixir** | mix.exs, mix.lock |
| **C/C++** | Makefile, CMakeLists.txt, configure.ac |

### Content-Based Detection

When file-based detection is inconclusive, examine file contents for clues:

#### Import/Package Statements
- Python: `import`, `from`, `pip install`
- Node.js: `require()`, `import`, `from`
- Rust: `use`, `extern crate`
- Go: `import`
- Java: `import`, `package`
- C#: `using`, `namespace`

#### Build Tool Indicators
- Look for build scripts: Makefile, build.sh, compile.sh
- Check for test directories: test/, tests/, __tests__/, spec/
- Examine CI/CD files: .github/workflows/, .gitlab-ci.yml, .travis.yml, Jenkinsfile

### Hierarchy of Detection

1. **Explicit project files** (highest confidence)
   - Package manifests: package.json, requirements.txt, etc.
   - Build configuration: pom.xml, build.gradle, etc.
   - Language-specific config: tsconfig.json, .babelrc, etc.

2. **Source file examination** (medium confidence)
   - File extensions in src/ directory
   - Import/require statements in source files
   - Test file patterns

3. **Directory structure** (lower confidence)
   - Standard layouts: src/, lib/, include/, bin/
   - Test organization: test/, spec/, specs/
   - Documentation: docs/, doc/, documentation/

### Confidence Scoring

Assign weights to different indicators:

- **Definitive indicators** (weight 3.0):
  - Language-specific package managers
  - Build files for compiled languages
  - Language-specific project files

- **Strong indicators** (weight 2.0):
  - Source file extensions (>.50% match)
  - Test framework configurations
  - CI/CD configuration files

- **Weak indicators** (weight 1.0):
  - Documentation mentioning technology
  - File extensions in non-source directories
  - Miscellaneous configuration files

### Special Cases

#### Monorepos
Look for:
- Multiple package manifests in subdirectories
- Lerna configuration (lerna.json)
- Yarn workspaces (packages/ directory)
- Nx workspace (nx.json)
- Bazel (WORKSPACE, BUILD files)

#### Polyglot Projects
When multiple languages are detected:
- Weight by file count and size
- Consider primary language by lines of code
- Note secondary languages for completeness

#### Framework Detection
Beyond language, detect frameworks:
- Web: React, Vue, Angular, Express, Django, Flask, Spring
- Mobile: React Native, Flutter, Ionic, Xamarin
- Data: Pandas, NumPy, TensorFlow, PyTorch
- Testing: Jest, Mocha, PyTest, JUnit, NUnit, RSpec

## Implementation Guidelines

### File Checking Order
Check in this order for early termination:
1. Package manifests (package.json, requirements.txt, etc.)
2. Language-specific project files (Cargo.toml, pom.xml, etc.)
3. Build configuration files
4. Source file sampling
5. Directory structure analysis

### Performance Optimization
For large repositories:
1. Limit file scans to reasonable depth (typically 3 levels)
2. Skip binary files and large directories (node_modules/, .git/, etc.)
3. Use file extensions as preliminary filters
4. Cache results for frequently accessed repositories

### Edge Cases
Handle these special scenarios:
- Empty repositories (no files yet)
- Template repositories (generate_from: true)
- Forked repositories (may have misleading files)
- Archived repositories (read-only)
- Template repositories (is_template: true)

## Examples

### Python Project Detection
Files present:
- requirements.txt
- setup.py
- src/myproject/
- tests/
Result: Python (high confidence)

### Node.js Project Detection
Files present:
- package.json
- src/index.js
- webpack.config.js
Result: Node.js (high confidence)

### Mixed Project Detection
Files present:
- Cargo.toml (Rust)
- package.json (Node.js frontend)
Analysis:
- Rust weight: 3.0 (Cargo.toml)
- Node.js weight: 2.0 (package.json) + 1.0 (frontend assets)
- Primary: Rust, Secondary: Node.js

## References

- [GitHub Linguist](https://github.com/github/linguist) - Language detection
- [SPDX License List](https://spdx.org/licenses/) - License identification
- [Semantic Versioning](https://semver.org/) - Version detection
- [Keep a Changelog](https://keepachangelog.com/) - Changelog format