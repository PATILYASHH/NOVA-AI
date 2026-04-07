"""
NOVA - Style Learner
Learns user's coding style, UI preferences, naming patterns,
theme choices, and project structure from existing repos.
Reuses learned patterns when building new things.
"""

import os
import re
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from collections import Counter, defaultdict
from pathlib import Path

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class StyleLearner:
    """
    Learns Yash's coding style by scanning repos:
    1. Color schemes / themes (dark/light, accent colors)
    2. UI patterns (component structure, layout preferences)
    3. Naming conventions (camelCase, snake_case, kebab-case)
    4. File/folder structure preferences
    5. Tech stack choices
    6. Code formatting patterns
    7. Common libraries/packages used
    8. Comment style
    9. Error handling patterns
    10. Project structure templates
    """

    SCAN_EXTENSIONS = {
        "frontend": [".html", ".css", ".scss", ".jsx", ".tsx", ".vue", ".svelte", ".dart"],
        "backend": [".py", ".js", ".ts", ".go", ".java", ".cs"],
        "config": [".json", ".yaml", ".yml", ".toml", ".env.example", ".xml"],
        "style": [".css", ".scss", ".less", ".styled.ts", ".styled.js"],
    }

    SKIP_DIRS = {
        "node_modules", ".git", "__pycache__", ".venv", "venv",
        "dist", "build", ".next", ".nuxt", ".dart_tool",
        "android", "ios", ".gradle", ".idea",
    }

    def __init__(self):
        self.profile_file = os.path.join(BASE_DIR, "intelligence", "data", "style_profile.json")
        self.profile = self._load()
        logger.info("Style Learner initialized")

    def _load(self) -> Dict:
        try:
            if os.path.exists(self.profile_file):
                with open(self.profile_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {
            "last_scan": None,
            "repos_scanned": [],
            "themes": {},
            "colors": {},
            "naming": {},
            "tech_stack": {},
            "packages": {},
            "file_patterns": {},
            "code_patterns": {},
            "ui_patterns": {},
            "project_structures": {},
            "preferences": {},
        }

    def _save(self):
        try:
            os.makedirs(os.path.dirname(self.profile_file), exist_ok=True)
            with open(self.profile_file, 'w', encoding='utf-8') as f:
                json.dump(self.profile, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save style profile: {e}")

    def scan_repo(self, repo_path: str) -> Dict:
        """Scan a repository and learn patterns"""
        if not os.path.exists(repo_path):
            return {"success": False, "error": f"Path not found: {repo_path}"}

        report = {
            "repo": repo_path,
            "name": os.path.basename(repo_path),
            "scanned_at": datetime.now().isoformat(),
            "files_scanned": 0,
            "patterns_found": {},
        }

        all_files = self._collect_files(repo_path)
        report["files_scanned"] = len(all_files)

        # Run all analyzers
        self._analyze_naming(all_files, repo_path)
        self._analyze_colors_and_themes(all_files, repo_path)
        self._analyze_tech_stack(all_files, repo_path)
        self._analyze_packages(repo_path)
        self._analyze_file_structure(repo_path)
        self._analyze_code_patterns(all_files, repo_path)
        self._analyze_ui_patterns(all_files, repo_path)

        # Record scan
        if repo_path not in self.profile["repos_scanned"]:
            self.profile["repos_scanned"].append(repo_path)
        self.profile["last_scan"] = datetime.now().isoformat()
        self._save()

        report["patterns_found"] = {
            "colors": len(self.profile.get("colors", {})),
            "naming_conventions": len(self.profile.get("naming", {})),
            "packages": len(self.profile.get("packages", {})),
            "code_patterns": len(self.profile.get("code_patterns", {})),
        }

        return {"success": True, "report": report}

    def scan_all_repos(self, base_path: str = "C:\\code") -> Dict:
        """Scan all repos under a base path"""
        results = []
        if not os.path.exists(base_path):
            return {"success": False, "error": f"Path not found: {base_path}"}

        for item in os.listdir(base_path):
            full_path = os.path.join(base_path, item)
            if os.path.isdir(full_path):
                git_dir = os.path.join(full_path, ".git")
                if os.path.exists(git_dir) or any(
                    os.path.exists(os.path.join(full_path, f))
                    for f in ["package.json", "pubspec.yaml", "requirements.txt", "setup.py"]
                ):
                    result = self.scan_repo(full_path)
                    results.append(result)

        return {
            "success": True,
            "repos_scanned": len(results),
            "results": results,
        }

    def _collect_files(self, repo_path: str, max_files: int = 500) -> List[str]:
        """Collect relevant files from repo"""
        files = []
        all_exts = set()
        for exts in self.SCAN_EXTENSIONS.values():
            all_exts.update(exts)

        for root, dirs, filenames in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in self.SKIP_DIRS]
            for f in filenames:
                ext = os.path.splitext(f)[1].lower()
                if ext in all_exts:
                    files.append(os.path.join(root, f))
                    if len(files) >= max_files:
                        return files
        return files

    def _analyze_naming(self, files: List[str], repo_path: str):
        """Analyze naming conventions"""
        naming = self.profile.setdefault("naming", {})
        file_names = []
        variable_names = []
        function_names = []

        for fp in files:
            fname = os.path.splitext(os.path.basename(fp))[0]
            file_names.append(fname)

            try:
                with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(5000)  # First 5KB

                # Python/JS function names
                funcs = re.findall(r'(?:def|function|const|let|var)\s+(\w+)', content)
                function_names.extend(funcs)

                # Variable names
                vars_found = re.findall(r'(?:let|const|var|self\.)\s*(\w+)\s*=', content)
                variable_names.extend(vars_found)

            except Exception:
                pass

        # Detect naming style
        def detect_style(names):
            if not names:
                return "unknown"
            styles = Counter()
            for name in names:
                if '_' in name:
                    styles["snake_case"] += 1
                elif name[0].isupper() and any(c.isupper() for c in name[1:]):
                    styles["PascalCase"] += 1
                elif name[0].islower() and any(c.isupper() for c in name[1:]):
                    styles["camelCase"] += 1
                elif '-' in name:
                    styles["kebab-case"] += 1
                elif name.islower():
                    styles["lowercase"] += 1
            return styles.most_common(1)[0][0] if styles else "unknown"

        naming["file_naming"] = detect_style(file_names)
        naming["function_naming"] = detect_style(function_names)
        naming["variable_naming"] = detect_style(variable_names)
        naming["sample_count"] = len(file_names) + len(function_names) + len(variable_names)

    def _analyze_colors_and_themes(self, files: List[str], repo_path: str):
        """Extract color schemes and theme preferences"""
        colors = self.profile.setdefault("colors", {})
        themes = self.profile.setdefault("themes", {})

        hex_colors = Counter()
        theme_indicators = {"dark": 0, "light": 0}

        for fp in files:
            ext = os.path.splitext(fp)[1].lower()
            if ext not in ['.css', '.scss', '.html', '.jsx', '.tsx', '.dart', '.js', '.ts', '.vue']:
                continue

            try:
                with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(10000)

                # Find hex colors
                found = re.findall(r'#([0-9a-fA-F]{3,8})\b', content)
                for c in found:
                    if len(c) in (3, 6, 8):
                        hex_colors[f"#{c.lower()}"] += 1

                # Theme detection
                content_lower = content.lower()
                if 'dark' in content_lower or 'background: #1' in content_lower or 'background: #0' in content_lower:
                    theme_indicators["dark"] += 1
                if 'light' in content_lower or 'background: #f' in content_lower or 'background: #e' in content_lower:
                    theme_indicators["light"] += 1

                # Look for theme variables
                if 'primaryColor' in content or 'primary-color' in content or 'primary_color' in content:
                    primary = re.findall(r'(?:primaryColor|primary-color|primary_color)\s*[:=]\s*["\']?(#[0-9a-fA-F]+)', content)
                    if primary:
                        colors["primary"] = primary[0]

                if 'backgroundColor' in content or 'background-color' in content:
                    bg = re.findall(r'(?:backgroundColor|background-color)\s*[:=]\s*["\']?(#[0-9a-fA-F]+)', content)
                    if bg:
                        colors["background"] = bg[0]

            except Exception:
                pass

        # Most used colors
        top_colors = hex_colors.most_common(10)
        colors["most_used"] = [{"color": c, "count": n} for c, n in top_colors]

        # Theme preference
        if theme_indicators["dark"] > theme_indicators["light"]:
            themes["preference"] = "dark"
        elif theme_indicators["light"] > theme_indicators["dark"]:
            themes["preference"] = "light"
        else:
            themes["preference"] = "dark"  # Yash prefers dark

        themes["dark_count"] = theme_indicators["dark"]
        themes["light_count"] = theme_indicators["light"]

    def _analyze_tech_stack(self, files: List[str], repo_path: str):
        """Detect tech stack from files"""
        stack = self.profile.setdefault("tech_stack", {})
        repo_name = os.path.basename(repo_path)
        detected = []

        # Check for config files
        checks = {
            "package.json": "Node.js",
            "pubspec.yaml": "Flutter/Dart",
            "requirements.txt": "Python",
            "setup.py": "Python",
            "Cargo.toml": "Rust",
            "go.mod": "Go",
            "pom.xml": "Java/Maven",
            "build.gradle": "Java/Gradle",
            "tsconfig.json": "TypeScript",
            "next.config.js": "Next.js",
            "nuxt.config.js": "Nuxt.js",
            "vue.config.js": "Vue.js",
            "angular.json": "Angular",
            ".env": "Env-based config",
        }

        for config_file, tech in checks.items():
            if os.path.exists(os.path.join(repo_path, config_file)):
                detected.append(tech)

        # Extension-based detection
        ext_counter = Counter(os.path.splitext(f)[1].lower() for f in files)
        if ext_counter.get('.dart', 0) > 5:
            detected.append("Dart")
        if ext_counter.get('.tsx', 0) > 0 or ext_counter.get('.jsx', 0) > 0:
            detected.append("React")
        if ext_counter.get('.vue', 0) > 0:
            detected.append("Vue")

        stack[repo_name] = list(set(detected))

    def _analyze_packages(self, repo_path: str):
        """Analyze commonly used packages"""
        packages = self.profile.setdefault("packages", {})

        # Node packages
        pkg_json = os.path.join(repo_path, "package.json")
        if os.path.exists(pkg_json):
            try:
                with open(pkg_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                deps = {}
                deps.update(data.get("dependencies", {}))
                deps.update(data.get("devDependencies", {}))
                for pkg in deps:
                    packages[pkg] = packages.get(pkg, 0) + 1
            except Exception:
                pass

        # Python packages
        req_txt = os.path.join(repo_path, "requirements.txt")
        if os.path.exists(req_txt):
            try:
                with open(req_txt, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            pkg = re.split(r'[>=<~!]', line)[0].strip()
                            if pkg:
                                packages[pkg] = packages.get(pkg, 0) + 1
            except Exception:
                pass

        # Flutter packages
        pubspec = os.path.join(repo_path, "pubspec.yaml")
        if os.path.exists(pubspec):
            try:
                with open(pubspec, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Simple YAML parsing for dependencies
                in_deps = False
                for line in content.split('\n'):
                    if line.strip() in ('dependencies:', 'dev_dependencies:'):
                        in_deps = True
                        continue
                    if in_deps and line.strip() and not line.startswith(' '):
                        in_deps = False
                    if in_deps and ':' in line:
                        pkg = line.split(':')[0].strip()
                        if pkg and not pkg.startswith('#'):
                            packages[pkg] = packages.get(pkg, 0) + 1
            except Exception:
                pass

    def _analyze_file_structure(self, repo_path: str):
        """Learn project structure patterns"""
        structures = self.profile.setdefault("file_patterns", {})
        repo_name = os.path.basename(repo_path)

        top_level = []
        try:
            for item in os.listdir(repo_path):
                if item.startswith('.'):
                    continue
                full = os.path.join(repo_path, item)
                if os.path.isdir(full) and item not in self.SKIP_DIRS:
                    top_level.append(f"{item}/")
                elif os.path.isfile(full):
                    top_level.append(item)
        except Exception:
            pass

        structures[repo_name] = sorted(top_level)

    def _analyze_code_patterns(self, files: List[str], repo_path: str):
        """Learn code patterns: error handling, imports, etc."""
        patterns = self.profile.setdefault("code_patterns", {})

        error_styles = Counter()
        import_styles = Counter()
        comment_styles = Counter()

        for fp in files[:100]:  # Limit to 100 files
            try:
                with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(5000)

                # Error handling style
                if 'try:' in content or 'try {' in content:
                    error_styles["try_catch"] += 1
                if '.catch(' in content:
                    error_styles["promise_catch"] += 1
                if 'if err != nil' in content:
                    error_styles["go_style"] += 1

                # Import style
                if 'from ' in content and ' import ' in content:
                    import_styles["python_from_import"] += 1
                if 'import ' in content and '{' in content:
                    import_styles["es6_destructured"] += 1
                if 'require(' in content:
                    import_styles["commonjs_require"] += 1

                # Comment style
                if '"""' in content or "'''" in content:
                    comment_styles["docstring"] += 1
                if '//' in content:
                    comment_styles["single_line_slash"] += 1
                if '#' in content:
                    comment_styles["hash_comment"] += 1
                if '/**' in content:
                    comment_styles["jsdoc"] += 1

            except Exception:
                pass

        patterns["error_handling"] = dict(error_styles.most_common(3))
        patterns["import_style"] = dict(import_styles.most_common(3))
        patterns["comment_style"] = dict(comment_styles.most_common(3))

    def _analyze_ui_patterns(self, files: List[str], repo_path: str):
        """Learn UI patterns: layout, component structure"""
        ui = self.profile.setdefault("ui_patterns", {})

        layout_patterns = Counter()
        component_patterns = Counter()

        for fp in files:
            ext = os.path.splitext(fp)[1].lower()
            if ext not in ['.html', '.jsx', '.tsx', '.vue', '.dart', '.css', '.scss']:
                continue

            try:
                with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(5000)

                # Layout detection
                if 'flexbox' in content.lower() or 'display: flex' in content:
                    layout_patterns["flexbox"] += 1
                if 'grid' in content.lower() or 'display: grid' in content:
                    layout_patterns["grid"] += 1
                if 'Container' in content or 'container' in content:
                    layout_patterns["container"] += 1
                if 'Column' in content or 'Row' in content:
                    layout_patterns["row_column"] += 1

                # Component patterns
                if 'class ' in content and 'extends' in content:
                    component_patterns["class_based"] += 1
                if 'function ' in content or '=>' in content:
                    component_patterns["functional"] += 1
                if 'StatefulWidget' in content or 'StatelessWidget' in content:
                    component_patterns["flutter_widget"] += 1

                # Border radius (rounded corners preference)
                radii = re.findall(r'border-radius:\s*(\d+)', content)
                radii += re.findall(r'BorderRadius\.circular\((\d+)', content)
                if radii:
                    ui["preferred_border_radius"] = max(set(radii), key=radii.count)

                # Font sizes
                fonts = re.findall(r'font-size:\s*(\d+)', content)
                if fonts:
                    ui["common_font_sizes"] = [int(f) for f in Counter(fonts).most_common(3)]

            except Exception:
                pass

        ui["layout_preference"] = dict(layout_patterns.most_common(3))
        ui["component_style"] = dict(component_patterns.most_common(3))

    def get_style_guide(self) -> str:
        """Generate a style guide from learned patterns"""
        if not self.profile.get("repos_scanned"):
            return "No repos scanned yet. Use /scanstyle to scan your projects."

        text = "**Yash's Coding Style Profile**\n\n"

        # Theme
        themes = self.profile.get("themes", {})
        if themes:
            text += f"**Theme Preference:** {themes.get('preference', 'dark')}\n"

        # Colors
        colors = self.profile.get("colors", {})
        if colors.get("primary"):
            text += f"**Primary Color:** {colors['primary']}\n"
        if colors.get("background"):
            text += f"**Background:** {colors['background']}\n"
        if colors.get("most_used"):
            top = colors["most_used"][:5]
            text += f"**Most Used Colors:** {', '.join(c['color'] for c in top)}\n"

        # Naming
        naming = self.profile.get("naming", {})
        if naming:
            text += f"\n**Naming Conventions:**\n"
            text += f"  Files: {naming.get('file_naming', 'N/A')}\n"
            text += f"  Functions: {naming.get('function_naming', 'N/A')}\n"
            text += f"  Variables: {naming.get('variable_naming', 'N/A')}\n"

        # Tech stack
        stack = self.profile.get("tech_stack", {})
        if stack:
            text += f"\n**Tech Stack:**\n"
            for repo, techs in stack.items():
                text += f"  {repo}: {', '.join(techs)}\n"

        # Packages
        packages = self.profile.get("packages", {})
        if packages:
            top_pkgs = sorted(packages.items(), key=lambda x: x[1], reverse=True)[:10]
            text += f"\n**Favorite Packages:**\n"
            for pkg, count in top_pkgs:
                text += f"  - {pkg} (used in {count} projects)\n"

        # Code patterns
        code = self.profile.get("code_patterns", {})
        if code:
            text += f"\n**Code Patterns:**\n"
            if code.get("error_handling"):
                text += f"  Error handling: {', '.join(code['error_handling'].keys())}\n"
            if code.get("import_style"):
                text += f"  Import style: {', '.join(code['import_style'].keys())}\n"

        # UI
        ui = self.profile.get("ui_patterns", {})
        if ui:
            text += f"\n**UI Patterns:**\n"
            if ui.get("layout_preference"):
                text += f"  Layout: {', '.join(ui['layout_preference'].keys())}\n"
            if ui.get("component_style"):
                text += f"  Components: {', '.join(ui['component_style'].keys())}\n"
            if ui.get("preferred_border_radius"):
                text += f"  Border radius: {ui['preferred_border_radius']}px\n"

        # Repos scanned
        text += f"\n**Repos Scanned:** {len(self.profile.get('repos_scanned', []))}\n"
        text += f"**Last Scan:** {self.profile.get('last_scan', 'Never')[:19]}\n"

        return text

    def get_recommendations_for(self, project_type: str) -> Dict:
        """Get style recommendations for a new project"""
        recs = {
            "theme": self.profile.get("themes", {}).get("preference", "dark"),
            "colors": {},
            "naming": self.profile.get("naming", {}),
            "suggested_packages": [],
            "structure": [],
        }

        colors = self.profile.get("colors", {})
        if colors.get("primary"):
            recs["colors"]["primary"] = colors["primary"]
        if colors.get("background"):
            recs["colors"]["background"] = colors["background"]

        # Suggest packages based on project type
        packages = self.profile.get("packages", {})
        type_lower = project_type.lower()
        if "flutter" in type_lower or "dart" in type_lower:
            recs["suggested_packages"] = [p for p in packages if packages[p] >= 1]
        elif "react" in type_lower or "next" in type_lower:
            recs["suggested_packages"] = [p for p in packages
                                           if packages[p] >= 1 and not p.startswith("flutter")]
        elif "python" in type_lower:
            recs["suggested_packages"] = [p for p in packages
                                           if packages[p] >= 1]

        return recs
