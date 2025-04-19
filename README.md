# GitHub Repository Statistics

A command line tool that analyzes GitHub repositories to provide statistics about lines of code, broken down by programming language.

## Installation

No installation necessary, just make sure the script is executable:

```bash
chmod +x github_repo_stats.py
```

## Requirements

- Python 3.6+
- Git command line tool installed and available in PATH

## Usage

Basic usage:
```bash
./github_repo_stats.py https://github.com/username/repo
```

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

You can combine options:
```bash
./github_repo_stats.py -v -d https://github.com/username/repo
```

Example:

```bash
./github_repo_stats.py https://github.com/dingran/web_reader
```

## Features

- Accepts a GitHub repository URL as input
- Clones the repository locally to a temporary directory
- Calculates lines of code statistics by language
- Displays statistics in a clear, formatted output
- Provides verbose mode with file-by-file breakdown of each language
- Option to include or exclude documentation files (excluded by default)
- Cleans up the temporary repository after analysis
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