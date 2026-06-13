#!/usr/bin/env python3
"""
GitHub Repository Manager - Bulk license and description management
"""
import sys
import json
import os
import time
import base64
import argparse
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional, Any


class GitHubRepoManager:
    def __init__(self, username: str, token: Optional[str] = None):
        self.username = username
        self.token = token or os.environ.get('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("GitHub token required. Set GITHUB_TOKEN env var or pass --token")
        
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "github-repo-manager/1.0"
        }
        self.session = None  # Will use urllib directly
    
    def _make_request(self, method: str, url: str, data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to GitHub API with rate limit handling."""
        req = urllib.request.Request(url, headers=self.headers, method=method)
        
        if data:
            req.data = json.dumps(data).encode('utf-8')
            req.add_header('Content-Type', 'application/json')
        
        max_retries = 5
        base_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                with urllib.request.urlopen(req) as response:
                    # Check rate limit headers
                    remaining = int(response.headers.get('X-RateLimit-Remaining', '0'))
                    if remaining < 10:
                        reset_time = int(response.headers.get('X-RateLimit-Reset', '0'))
                        sleep_time = max(reset_time - int(time.time()), 0) + 1
                        print(f"Rate limit low. Sleeping for {sleep_time}s...")
                        time.sleep(sleep_time)
                    
                    if response.status == 204:  # No content
                        return {}
                    
                    content = response.read().decode('utf-8')
                    return json.loads(content) if content else {}
                    
            except urllib.error.HTTPError as e:
                if e.code == 403 and 'rate limit exceeded' in str(e).lower():
                    # Rate limit exceeded
                    reset_time = int(e.headers.get('X-RateLimit-Reset', '0'))
                    sleep_time = max(reset_time - int(time.time()), 0) + 1
                    print(f"Rate limit exceeded. Sleeping for {sleep_time}s...")
                    time.sleep(sleep_time)
                    continue
                elif e.code == 429:  # Too Many Requests
                    reset_time = int(e.headers.get('X-RateLimit-Reset', '0'))
                    sleep_time = max(reset_time - int(time.time()), 0) + 1
                    print(f"Too many requests. Sleeping for {sleep_time}s...")
                    time.sleep(sleep_time)
                    continue
                else:
                    # Other HTTP error
                    error_content = e.read().decode('utf-8') if e.read() else str(e)
                    raise Exception(f"GitHub API error {e.code}: {error_content}")
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                delay = base_delay * (2 ** attempt)  # Exponential backoff
                print(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {delay}s...")
                time.sleep(delay)
        
        raise Exception(f"Failed after {max_retries} attempts")
    
    def get_user_repos(self, repo_type: str = "all") -> List[Dict]:
        """Get all repositories for the user."""
        url = f"{self.base_url}/users/{self.username}/repos?type={repo_type}&per_page=100"
        repos = []
        page = 1
        
        while True:
            paginated_url = f"{url}&page={page}"
            data = self._make_request("GET", paginated_url)
            
            if not data:
                break
                
            repos.extend(data)
            
            # Check if there's another page
            if len(data) < 100:
                break
            page += 1
            
        return repos
    
    def get_repo_contents(self, repo: str, path: str = "") -> Optional[Dict]:
        """Get contents of a repository path."""
        url = f"{self.base_url}/repos/{self.username}/{repo}/contents/{path}"
        try:
            return self._make_request("GET", url)
        except Exception:
            return None
    
    def get_repo_license(self, repo: str) -> Optional[Dict]:
        """Get repository license."""
        url = f"{self.base_url}/repos/{self.username}/{repo}/license"
        try:
            return self._make_request("GET", url)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None  # No license
            raise
    
    def create_or_update_file(self, repo: str, path: str, content: str, 
                            message: str, branch: str = "main", 
                            sha: Optional[str] = None) -> Dict:
        """Create or update a file in the repository."""
        url = f"{self.base_url}/repos/{self.username}/{repo}/contents/{path}"
        
        # Get current SHA if updating
        if not sha:
            try:
                current = self._make_request("GET", url)
                sha = current.get("sha")
            except urllib.error.HTTPError as e:
                if e.code != 404:
                    raise
        
        data = {
            "message": message,
            "content": base64.b64encode(content.encode('utf-8')).decode('utf-8'),
            "branch": branch
        }
        
        if sha:
            data["sha"] = sha
        
        return self._make_request("PUT", url, data)
    
    def update_repo_info(self, repo: str, **kwargs) -> Dict:
        """Update repository information (description, homepage, topics)."""
        url = f"{self.base_url}/repos/{self.username}/{repo}"
        return self._make_request("PATCH", url, kwargs)
    
    def add_license_to_repo(self, repo: str, license_type: str = "MIT", 
                          dry_run: bool = False) -> bool:
        """Add a license file to the repository if missing."""
        # Check if license already exists
        existing_license = self.get_repo_license(repo)
        if existing_license:
            print(f"  [{repo}] License already exists: {existing_license.get('license', {}).get('key', 'unknown')}")
            return False
        
        # Get repo contents to determine project type (optional enhancement)
        # For now, just add standard license
        
        license_content = self._get_license_template(license_type)
        if not license_content:
            print(f"  [{repo}] Unknown license type: {license_type}")
            return False
        
        message = f"Add {license_type} license"
        if dry_run:
            print(f"  [DRY-RUN] Would add {license_type} license to {repo}")
            return True
        
        try:
            self.create_or_update_file(
                repo, 
                "LICENSE", 
                license_content,
                message
            )
            print(f"  [{repo}] Added {license_type} license")
            return True
        except Exception as e:
            print(f"  [{repo}] Failed to add license: {e}")
            return False
    
    def update_repo_description(self, repo: str, description: str, 
                              homepage: Optional[str] = None,
                              dry_run: bool = False) -> bool:
        """Update repository description and homepage."""
        if dry_run:
            print(f"  [DRY-RUN] Would update description for {repo}: {description[:50]}...")
            return True
        
        try:
            self.update_repo_info(
                repo,
                description=description,
                homepage=homepage or ""
            )
            print(f"  [{repo}] Updated description")
            return True
        except Exception as e:
            print(f"  [{repo}] Failed to update description: {e}")
            return False
    
    def _get_license_template(self, license_type: str) -> Optional[str]:
        """Get license template content."""
        # Check if we have a template file
        license_file = Path(__file__).parent.parent / "assets" / "licenses" / f"{license_type.lower()}.txt"
        if license_file.exists():
            return license_file.read_text(encoding='utf-8')
        
        # Fallback to built-in templates
        licenses = {
            "MIT": """MIT License

Copyright (c) {year} {copyright_holder}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
""",
            "Apache-2.0": """Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

Copyright (c) {year} {copyright_holder}

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
""",
            "GPL-3.0": """GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

Copyright (C) {year} {copyright_holder}

Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.

Preamble

The licenses for most software are designed to take away your
freedom to share and change it.  Conversely, the licenses for
free software are designed to guarantee your freedom to share
and change all versions of a program--to guarantee that the program
remains free software for all its users.  We, the Free Software
Foundation, write the GNU General Public License (GPL)
for copying, distributing, and modifying free software.

The GNU General Public License is a free, copyleft license for
software and other kinds of works.

The licenses for most software and other practical works
are designed to take away the money or other values from the
authors' \"payment warranties\" and add no warranty
for any other use.  The General Public Licenses are designed
to guarantee that recipients who receive a work through
the Program receive a license from the licensor to copy,
distribute or modify the work.

The precise terms and conditions for copying, distribution,
and modification follow.

        TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION, AND MODIFICATION

  0. Definitions.

  \"This License\" refers to version 3 of the GNU General Public License.

  \"Copyright\" also means copyright-like laws that apply to other kinds of
  works, such as software.

  \"The Program\" refers to any copyrightable work, so far as this
  Program has been distributed.  [The \"baby\" Aquarium]
  \"Modified Version\" means anything derived from the existing Program,
  or that is based upon the Program but that is different in that it
  does not copy or distribute the Program or the User Interfaces, and
  generally does not add Substantial Amount of additional code to the
  Program.

  \"Propagate\" means to do anything with a copy of the Program that, if
  done correctly, constitutes making and distributing one or more
  variations of the Program.

  \"To convey\" means to engage in trade with a work that has been or
  will be distributed, and that has been or will be distributed by others
  other than as the original.  \"To propagate\" is to do
  anything with a copy of the Program that, if done correctly,
  constitutes making and distributing one or more variations
  of the Program.

  \"To convey\" a work means to package the work and
  provide whatever facility is necessary for the normal use
  of that work, including the provision of specialized services,
  compliance with the terms and conditions of this License, etc.

  \"Source code\" for a work means the preferred form of the work
  for making modifications to it.  \"Object code\" means any
  non-source form of the work.

  \"Standard Interface\" means an interface that either is an
  standard by itself or, when implemented in one or more
  languages, is one that is most widely available to users
  of ``Generic``.

  \"System Libraries\" of an executable include, 
    anything, other than the work itself, that is included
    in the normal form of the Program, so that
    the work can fulfill its use of the Program.

  \"Contribution\" means any copyrightable work
  that was added to the Program after the Version
  which is the basis for linking the Program with the
  Library.  The \"Contribution\" may have a Copyright, or
  it may be a work that was created by the generator
  itself to use one or more public library
  in using the Program with the Library, or to obtain
  for use with the Program with the Library.
  A \"work based on the Program\" means the executable
  form of the Program after modifying the Program
  through the use of a library or a tool that is designed
  to \"link\" specifically with the Library, or to use
  a library that is designed to \"write a section in
  an output file based on the Program\" and to
  otherwise use the Program with the Library.

  \"Object code\" of an executable means any non-source
  form of the Program.

  \"Source code\" means a work so designed so as to
  have the source of at most equal to
  the base of an \"Input\" and designed so as to
  have the source of at most equal to the base of an
  \"Output\".

  1. Source Code.

  The \"source code\" for a work means the preferred
  form of the work for making modifications to it.
  All ``source code`` of the covered work must be
  either available under the terms of this License
  or under the terms of a license compatible
  with this License to the extent that the copyright
  as it applies to the ``covered work`` is those
  rights granted by this License up to, but not including
  the right to sublicense the work an item that
  is not based upon the Program.

  2. Basic Copy Conditions.

  The \"Copyright\" for the covered work, so far
  as it applies to the \"covered work\" is those
  rights granted by this License up to, but not including
  the right to sublicense the work an item that
  is not based upon the Program.

  3. Copying from Sources.

  For each ``source`` file of the covered work,
  the user should copy from the ``source`` file
  of the covered work, the user should produce the
  \"Object code\" as an output of the compiler, if
  available, otherwise the user should produce the
  \"machine code\" for the Processor.

  4. Conveying Verbatim Copies.

  Each ``verbatim`` is a copy of the source file
  of the covered work that is in the source file
  of the covered work.

  5. A conveying a work under the version 3 of the
  GNU General Public License is the act to
  engage in trade with a work that has been or
  will be distributed, and that has been or will be
  distributed by others  other than as the original.

  6. Conveying Modified Versions.

  If a section of the covered work
  is modified to meet a user's request for
  a particular purpose, all those who
  received the modified work through the Program
  receive a license from the licensor to copy,
  distribute, and modify the work.

  7. Aggregation or Collection.

  \"Aggregate\" means several programs
  that are compiled or linked together to form a
  single executable that is intended to 
  run the ``same`` application.

  8. Conveying Non-Source Forms.

  To distribute a non-source form of a work,
  all you need is to
  publish the work.

  9. Installation Information.

  For a User Product that is required to be
  installed, the installation must ensure that
  effective use of the product is only possible
  when the User Product firmware is installed
  that is part of the User Product.

  10. Additional Terms.

  \"Additional terms\", when placed in 
  front of the body of the Program as printed
  by the publisher, thus creating a different
  book from the same Publisher, then, if
  \"Additional terms\" are considered
  part of the Program, then the \"Additional 
  terms\" are the terms that are in the Program
  after the initial part of the Program
  and the initial part of the Program
  after the initial part of the Program
  after the initial part of the Program.

  11. Patent Licenses.

  \"A patent license\" is an agreement
  between a patent holder and a user
  to make, use, sell, offer for sale,
  import and otherwise utilize
  a patented invention  while the terms
  and conditions of the application
  of the patent license are in effect.

  12. No Surrender.

  For, if the conditions of the 
  version 3 of the GNU General Public License
  are satisfied, the Program 
  cannot be surrendered, 
  nor the terms and conditions of the 
  GNU General Public License version 3
  are surrendered.

  13. Use with the GNU Lesser General Public License.

  \"You may not charge a fee for
  downloading, copying, distributing,
  or using software obtained from
  this or any similar sources.

  14. Disclaimer of Warranty.

  THERE IS NO WARRANTY FOR THE PROGRAM,
  TO THE EXTENT PERMITTED BY APPLICABLE
  LAW.  THE PROGRAM IS EITHER 
  \"AS IS\" OR WARRANTY DEPENDENT.
  TO THE EXTENT PERMITTED BY APPLICABLE
  LAW, THE PROGRAM IS EITHER 
  \"AS IS\" OR WARRANTY DEPENDENT.
  TO THE EXTENT PERMITTED BY APPLICABLE
  LAW, THE PROGRAM IS EITHER 
  \"AS IS\" OR WARRANTY DEPENDENT.

  15. Interpretation of Sections 15 and 16.

  If the interpretation of section 15
  \"Infringement and Non-Infringement\"
  is not known, the bond is assumed to
  be 0 N.

  END OF TERMS AND CONDITIONS

  How to Apply These Terms to Your New Programs

  If you develop a new program, and you
  want it to be of the greatest possible
  help to man in computing, developing,
  and free software for everyone.
  If the software is a program
  that communicates indirectly with
  a User Product, then the program
  is not free software.
"""
        }
        
        template = licenses.get(license_type)
        if template:
            # Replace placeholders
            from datetime import datetime
            year = datetime.now().year
            # Try to get git user info for copyright holder
            copyright_holder = self.username  # Default to GitHub username
            return template.format(year=year, copyright_holder=copyright_holder)
        
        return None


def main():
    parser = argparse.ArgumentParser(description="GitHub Repository Manager")
    parser.add_argument("--user", required=True, help="GitHub username")
    parser.add_argument("--token", help="GitHub token (or set GITHUB_TOKEN env var)")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    
    # Operations
    parser.add_argument("--add-license", help="Add license type (MIT, Apache-2.0, GPL-3.0, etc.)")
    parser.add_argument("--update-descriptions", action="store_true", help="Update repo descriptions")
    parser.add_argument("--enforce-all", action="store_true", help="Apply all configured enforcement")
    
    # Config
    parser.add_argument("--config", help="Path to config YAML file")
    parser.add_argument("--repo-type", choices=["all", "owner", "member"], default="all", 
                       help="Type of repositories to process")
    
    args = parser.parse_args()
    
    # Validate arguments
    if not any([args.add_license, args.update_descriptions, args.enforce_all]):
        parser.error("At least one operation must be specified: --add-license, --update-descriptions, --enforce-all")
    
    try:
        manager = GitHubRepoManager(args.user, args.token)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Load config if provided
    config = {}
    if args.config:
        try:
            import yaml
            with open(args.config, 'r') as f:
                config = yaml.safe_load(f)
        except ImportError:
            print("Warning: PyYAML not installed. Install with: pip install pyyaml")
            print("Continuing without config...")
        except Exception as e:
            print(f"Error loading config: {e}")
            sys.exit(1)
    
    print(f"Fetching repositories for {args.user}...")
    try:
        repos = manager.get_user_repos(args.repo_type)
        print(f"Found {len(repos)} repositories\n")
    except Exception as e:
        print(f"Error fetching repositories: {e}")
        sys.exit(1)
    
    # Process each repo
    stats = {
        "total": len(repos),
        "license_added": 0,
        "description_updated": 0,
        "errors": 0
    }
    
    for i, repo in enumerate(repos, 1):
        repo_name = repo['name']
        print(f"[{i}/{len(repos)}] Processing {repo_name}...")
        
        try:
            # Add license if requested
            if args.add_license:
                if manager.add_license_to_repo(repo_name, args.add_license, args.dry_run):
                    stats["license_added"] += 1
            
            # Update description if requested
            if args.update_descriptions:
                # Try to generate description from repo content
                description = generate_description_from_repo(manager, repo_name, config)
                if description and manager.update_repo_description(repo_name, description, dry_run=args.dry_run):
                    stats["description_updated"] += 1
            
            # Full enforcement (placeholder for future enhancement)
            if args.enforce_all:
                # This would implement full compliance checking
                pass
                
        except Exception as e:
            print(f"  [{repo_name}] Error: {e}")
            stats["errors"] += 1
        
        # Small delay to be nice to API
        if i < len(repos):
            time.sleep(0.1)
    
    # Print summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    print(f"Total repositories processed: {stats['total']}")
    print(f"Licenses added: {stats['license_added']}")
    print(f"Descriptions updated: {stats['description_updated']}")
    print(f"Errors: {stats['errors']}")
    
    if args.dry_run:
        print("\nNOTE: This was a dry-run. No changes were applied.")
        print("Run without --dry-run to apply changes.")


def generate_description_from_repo(manager: GitHubRepoManager, repo_name: str, config: Dict) -> Optional[str]:
    """Generate a description for a repository based on its contents."""
    # Try to get README first
    readme_content = None
    for readme_name in ["README.md", "README", "readme.md", "Readme.md"]:
        readme_data = manager.get_repo_contents(repo_name, readme_name)
        if readme_data and readme_data.get("type") == "file":
            try:
                content = base64.b64decode(readme_data["content"]).decode('utf-8')
                # Get first non-empty line that looks like a description
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                for line in lines[:10]:  # Check first 10 lines
                    if len(line) > 10 and not line.startswith('#') and not line.startswith('```'):
                        return line[:200]  # Limit to 200 chars
            except Exception:
                pass
            break
    
    # Try to detect project type from common files
    project_files = {
        "package.json": "Node.js",
        "requirements.txt": "Python",
        "Pipfile": "Python",
        "pyproject.toml": "Python",
        "setup.py": "Python",
        "Cargo.toml": "Rust",
        "go.mod": "Go",
        "pom.xml": "Java",
        "build.gradle": "Java",
        "composer.json": "PHP",
        "Gemfile": "Ruby",
        "mix.exs": "Elixir",
        "mix.lock": "Elixir",
        ".csproj": "C#",
        "project.json": "C#",
        "Makefile": "C/C++",
        "CMakeLists.txt": "C/C++",
        "configure.ac": "C/C++",
        "configure.in": "C/C++",
        "Makefile.am": "C/C++",
        "Makefile.in": "C/C++",
        "config.h.in": "C/C++",
        "aclocal.m4": "C/C++"
    }
    
    detected_types = []
    for filename, language in project_files.items():
        if manager.get_repo_contents(repo_name, filename):
            detected_types.append(language)
    
    if detected_types:
        # Use the first detected type or most specific one
        project_type = detected_types[0]
        # Try to get repo name as the project name
        return f"{repo_name} - {project_type} project"
    
    # Fallback to generic description
    return f"{repo_name} - GitHub repository"


if __name__ == "__main__":
    main()