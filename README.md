# GitHub Repository Statistics

A command line tool that analyzes GitHub repositories or local code directories to provide statistics about lines of code, broken down by programming language.

## Installation

No installation necessary, just make sure the script is executable:

```bash
chmod +x github_repo_stats.py
```

## Requirements

- Python 3.6+
- Git command line tool installed and available in PATH (only needed for GitHub repository analysis)

## Usage

### Analyzing GitHub Repositories

Basic usage:
```bash
./github_repo_stats.py https://github.com/username/repo
```

### Analyzing Local Directories

For local repositories or code directories:
```bash
./github_repo_stats.py /path/to/your/code
```

Or explicitly specify the local flag:
```bash
./github_repo_stats.py -l /path/to/your/code
```

### Options

Verbose mode (shows breakdown by filenames):
```bash
./github_repo_stats.py -v https://github.com/username/repo
```
or
```bash
./github_repo_stats.py --verbose https://github.com/username/repo
```

Include documentation files (Markdown, RST, etc.):
```bash
./github_repo_stats.py -d https://github.com/username/repo
```
or
```bash
./github_repo_stats.py --include-docs https://github.com/username/repo
```

Exclude specific files or directories (using glob patterns):
```bash
./github_repo_stats.py -e "src/test/*" https://github.com/username/repo
```
or
```bash
./github_repo_stats.py --exclude "src/test/*" https://github.com/username/repo
```

You can specify multiple exclusion patterns:
```bash
./github_repo_stats.py -e "src/test/*" -e "*.min.js" https://github.com/username/repo
```

You can combine all options:
```bash
./github_repo_stats.py -v -d -e "src/test/*" https://github.com/username/repo
```

Local directory example:
```bash
./github_repo_stats.py -v -e "node_modules/*" ~/projects/my-app
```

## Features

- Accepts a GitHub repository URL or local directory path as input
- Clones GitHub repositories to a temporary directory (if needed)
- Calculates lines of code statistics by language
- Displays statistics in a clear, formatted output
- Provides verbose mode with file-by-file breakdown of each language
- Option to include or exclude documentation files (excluded by default)
- Option to exclude specific files or directories using glob patterns
- Cleans up temporary repositories after analysis
- Handles common error cases gracefully

## Output Example

Basic output:
```
Repository: username/repo
Total Lines of Code: 1,234

Language Breakdown:
Python:      850 lines (68.9%)
JavaScript:  300 lines (24.3%)
HTML:         84 lines (6.8%)
```

Verbose output additionally shows:
```
  Top files:
    src/main.py                                          350 lines (41.2%)
    src/utils.py                                         200 lines (23.5%)
    src/models.py                                        150 lines (17.6%)
    ... and 5 more files
```

## Limitations

- Binary files are not analyzed
- Some specialized file types may not be recognized
- Large repositories may take longer to analyze 