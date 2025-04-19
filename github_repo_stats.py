#!/usr/bin/env python3

import os
import sys
import subprocess
import shutil
import tempfile
import re
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


def get_language_stats(repo_dir, verbose=False):
    """Calculate lines of code statistics by language."""
    language_extensions = {
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
        '.md': 'Markdown',
        '.json': 'JSON',
        '.xml': 'XML',
        '.yml': 'YAML',
        '.yaml': 'YAML',
    }
    
    # Define directories to exclude
    exclude_dirs = {'.git', 'node_modules', 'venv', 'env', '__pycache__', 'dist', 'build'}
    
    # Stats collection
    stats = defaultdict(int)
    total_lines = 0
    file_stats = defaultdict(dict)
    
    for root, dirs, files in os.walk(repo_dir):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            file_path = os.path.join(root, file)
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


def print_stats(repo_url, stats, total_lines, verbose=False, file_stats=None):
    """Print the statistics in a formatted way."""
    # Extract repo name from URL
    repo_name = repo_url.rstrip('/').split('/')[-2:]
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
    parser.add_argument("repo_url", help="GitHub repository URL")
    parser.add_argument("-v", "--verbose", action="store_true", 
                        help="Display detailed breakdown by files for each language")
    args = parser.parse_args()
    
    repo_url = args.repo_url
    verbose = args.verbose
    
    # Remove @ prefix if present (from example)
    if repo_url.startswith('@'):
        repo_url = repo_url[1:]
    
    # Validate URL
    if not validate_github_url(repo_url):
        print("Error: Invalid GitHub repository URL")
        sys.exit(1)
    
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        print(f"Cloning repository {repo_url}...")
        if not clone_repository(repo_url, temp_dir):
            sys.exit(1)
        
        print("Analyzing code statistics...")
        if verbose:
            stats, total_lines, file_stats = get_language_stats(temp_dir, verbose=True)
            print_stats(repo_url, stats, total_lines, verbose=True, file_stats=file_stats)
        else:
            stats, total_lines = get_language_stats(temp_dir)
            print_stats(repo_url, stats, total_lines)
        
    finally:
        # Clean up the temporary directory
        print(f"\nCleaning up temporary files...")
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main() 