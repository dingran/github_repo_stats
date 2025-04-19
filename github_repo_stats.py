#!/usr/bin/env python3

import os
import sys
import subprocess
import shutil
import tempfile
import re
import fnmatch
from urllib.parse import urlparse
from collections import defaultdict
import argparse


def validate_github_url(url):
    """Validate if the provided URL is a GitHub repository URL."""
    parsed_url = urlparse(url)
    
    # Check if the domain is github.com
    if parsed_url.netloc != "github.com":
        return False
    
    # Check if the path has at least two components (username/repo)
    path_parts = [part for part in parsed_url.path.split('/') if part]
    if len(path_parts) < 2:
        return False
    
    return True


def is_local_path(path):
    """Check if the provided path is a local directory."""
    return os.path.isdir(path)


def clone_repository(url, temp_dir):
    """Clone the GitHub repository to a temporary directory."""
    try:
        subprocess.run(["git", "clone", url, temp_dir], 
                      check=True, 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e}")
        return False


def should_exclude_path(path, exclude_patterns, repo_dir):
    """Check if a path should be excluded based on patterns."""
    if not exclude_patterns:
        return False
    
    rel_path = os.path.relpath(path, repo_dir)
    
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(rel_path, pattern):
            return True
    
    return False


def get_language_stats(repo_dir, verbose=False, include_docs=False, exclude_patterns=None):
    """Calculate lines of code statistics by language."""
    # Define code and documentation file extensions
    code_extensions = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.jsx': 'JavaScript',
        '.ts': 'TypeScript',
        '.tsx': 'TypeScript',
        '.html': 'HTML',
        '.css': 'CSS',
        '.scss': 'SCSS',
        '.sass': 'SASS',
        '.java': 'Java',
        '.c': 'C',
        '.cpp': 'C++',
        '.cs': 'C#',
        '.go': 'Go',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.rs': 'Rust',
        '.sh': 'Shell',
        '.json': 'JSON',
        '.xml': 'XML',
        '.yml': 'YAML',
        '.yaml': 'YAML',
    }
    
    # Define documentation file extensions
    doc_extensions = {
        '.md': 'Markdown',
        '.rst': 'ReStructuredText',
        '.txt': 'Text',
    }
    
    # Combine extensions based on user preference
    language_extensions = code_extensions.copy()
    if include_docs:
        language_extensions.update(doc_extensions)
    
    # Define directories to exclude
    exclude_dirs = {'.git', 'node_modules', 'venv', 'env', '__pycache__', 'dist', 'build'}
    
    # Stats collection
    stats = defaultdict(int)
    total_lines = 0
    file_stats = defaultdict(dict)
    
    for root, dirs, files in os.walk(repo_dir):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not should_exclude_path(os.path.join(root, d), exclude_patterns, repo_dir)]
        
        for file in files:
            file_path = os.path.join(root, file)
            
            # Skip excluded files
            if should_exclude_path(file_path, exclude_patterns, repo_dir):
                continue
                
            _, ext = os.path.splitext(file)
            
            if ext in language_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        line_count = sum(1 for _ in f)
                        language = language_extensions[ext]
                        stats[language] += line_count
                        total_lines += line_count
                        
                        if verbose:
                            # Get relative path from the repo root
                            rel_path = os.path.relpath(file_path, repo_dir)
                            file_stats[language][rel_path] = line_count
                except Exception:
                    # Skip files that can't be read
                    pass
    
    if verbose:
        return stats, total_lines, file_stats
    return stats, total_lines


def print_stats(repo_path, stats, total_lines, verbose=False, file_stats=None, is_local=False):
    """Print the statistics in a formatted way."""
    # Extract repo name from URL or use the directory name for local paths
    if is_local:
        repo_name = os.path.basename(os.path.abspath(repo_path))
    else:
        repo_name = repo_path.rstrip('/').split('/')[-2:]
        repo_name = '/'.join(repo_name)
    
    print(f"\nRepository: {repo_name}")
    print(f"Total Lines of Code: {total_lines:,}")
    
    if total_lines > 0:
        print("\nLanguage Breakdown:")
        # Sort languages by lines of code (descending)
        sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
        
        for language, lines in sorted_stats:
            percentage = (lines / total_lines) * 100
            print(f"{language:12} {lines:,} lines ({percentage:.1f}%)")
            
            if verbose and language in file_stats:
                # Sort files by line count (descending)
                sorted_files = sorted(file_stats[language].items(), key=lambda x: x[1], reverse=True)
                
                # Print top files for this language (limited to top 10 for clarity)
                print("\n  Top files:")
                for file_path, file_lines in sorted_files[:10]:
                    file_percentage = (file_lines / lines) * 100
                    print(f"    {file_path:<50} {file_lines:,} lines ({file_percentage:.1f}%)")
                
                # If there are more files, show a summary
                if len(sorted_files) > 10:
                    remaining = len(sorted_files) - 10
                    print(f"    ... and {remaining} more files")
                
                print()  # Extra line for readability


def main():
    parser = argparse.ArgumentParser(description="Analyze GitHub repository for code statistics")
    parser.add_argument("repo_path", help="GitHub repository URL or local directory path")
    parser.add_argument("-v", "--verbose", action="store_true", 
                        help="Display detailed breakdown by files for each language")
    parser.add_argument("-d", "--include-docs", action="store_true",
                        help="Include documentation files (Markdown, RST, etc.) in the analysis")
    parser.add_argument("-e", "--exclude", action="append", 
                        help="Exclude files/directories matching these patterns (can be used multiple times)")
    parser.add_argument("-l", "--local", action="store_true",
                        help="Analyze local directory instead of GitHub repository URL")
    args = parser.parse_args()
    
    repo_path = args.repo_path
    verbose = args.verbose
    include_docs = args.include_docs
    exclude_patterns = args.exclude
    is_local = args.local
    
    # Determine if it's a local path or if user explicitly specified local mode
    if is_local or is_local_path(repo_path):
        is_local = True  # Set to true if either flag is true or path is local
        
        if not os.path.isdir(repo_path):
            print(f"Error: The specified path '{repo_path}' is not a directory")
            sys.exit(1)
            
        print(f"Analyzing local directory: {repo_path}")
        
        stats_args = {
            'verbose': verbose,
            'include_docs': include_docs,
            'exclude_patterns': exclude_patterns
        }
        
        if verbose:
            stats, total_lines, file_stats = get_language_stats(repo_path, **stats_args)
            print_stats(repo_path, stats, total_lines, verbose=True, file_stats=file_stats, is_local=True)
        else:
            stats, total_lines = get_language_stats(repo_path, **stats_args)
            print_stats(repo_path, stats, total_lines, is_local=True)
            
    else:
        # Remove @ prefix if present (from example)
        if repo_path.startswith('@'):
            repo_path = repo_path[1:]
        
        # Validate URL
        if not validate_github_url(repo_path):
            print("Error: Invalid GitHub repository URL")
            sys.exit(1)
        
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        
        try:
            print(f"Cloning repository {repo_path}...")
            if not clone_repository(repo_path, temp_dir):
                sys.exit(1)
            
            print("Analyzing code statistics...")
            
            stats_args = {
                'verbose': verbose,
                'include_docs': include_docs,
                'exclude_patterns': exclude_patterns
            }
            
            if verbose:
                stats, total_lines, file_stats = get_language_stats(temp_dir, **stats_args)
                print_stats(repo_path, stats, total_lines, verbose=True, file_stats=file_stats)
            else:
                stats, total_lines = get_language_stats(temp_dir, **stats_args)
                print_stats(repo_path, stats, total_lines)
            
        finally:
            # Clean up the temporary directory
            print(f"\nCleaning up temporary files...")
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main() 