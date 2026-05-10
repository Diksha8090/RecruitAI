import requests
import os
import re
from typing import Dict, Optional

try:
    from github import Github
    PYGITHUB_AVAILABLE = True
except ImportError:
    PYGITHUB_AVAILABLE = False

class GitHubAnalyzer:
    """Extract and analyze GitHub profile from resume"""

    def __init__(self):
        self.token = os.getenv('GITHUB_TOKEN', '')
        self.headers = {'Authorization': f'token {self.token}'} if self.token else {}
        self.base_url = 'https://api.github.com'

    def extract_github_url(self, text: str) -> Optional[str]:
        patterns = [
            r'github\.com/([a-zA-Z0-9_-]+)',
            r'https?://github\.com/([a-zA-Z0-9_-]+)',
        ]
        for pat in patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                username = match.group(1).split('/')[0].strip()
                if username and username.lower() not in ['features', 'about', 'topics', 'trending']:
                    return f"https://github.com/{username}"
        return None

    def analyze(self, github_url: str) -> Dict:
        username = github_url.rstrip('/').split('/')[-1]
        try:
            user = self._get_user(username)
            repos = self._get_repos(username)
            languages = self._aggregate_languages(repos)
            top_repos = self._top_repos(repos)
            activity_score = self._activity_score(user, repos)

            return {
                'username': username,
                'url': github_url,
                'name': user.get('name', username),
                'bio': user.get('bio', ''),
                'public_repos': user.get('public_repos', 0),
                'followers': user.get('followers', 0),
                'following': user.get('following', 0),
                'total_stars': sum(r.get('stargazers_count', 0) for r in repos),
                'languages': languages,
                'top_repos': top_repos,
                'activity_score': activity_score,
                'github_score': self._compute_score(user, repos, activity_score),
                'account_created': user.get('created_at', ''),
                'last_active': user.get('updated_at', ''),
                'error': None
            }
        except Exception as e:
            return {'username': username, 'url': github_url, 'error': str(e), 'github_score': 0}

    def _get_user(self, username: str) -> Dict:
        r = requests.get(f'{self.base_url}/users/{username}', headers=self.headers, timeout=10)
        r.raise_for_status()
        return r.json()

    def _get_repos(self, username: str) -> list:
        r = requests.get(
            f'{self.base_url}/users/{username}/repos',
            headers=self.headers,
            params={'sort': 'updated', 'per_page': 30},
            timeout=10
        )
        r.raise_for_status()
        return r.json()

    def _aggregate_languages(self, repos: list) -> Dict:
        lang_count = {}
        for repo in repos:
            lang = repo.get('language')
            if lang:
                lang_count[lang] = lang_count.get(lang, 0) + 1
        total = sum(lang_count.values()) or 1
        return {lang: round(count / total * 100) for lang, count in
                sorted(lang_count.items(), key=lambda x: -x[1])[:8]}

    def _top_repos(self, repos: list) -> list:
        sorted_repos = sorted(repos, key=lambda r: r.get('stargazers_count', 0), reverse=True)
        return [
            {
                'name': r['name'],
                'description': r.get('description', ''),
                'stars': r.get('stargazers_count', 0),
                'forks': r.get('forks_count', 0),
                'language': r.get('language', ''),
                'url': r.get('html_url', '')
            }
            for r in sorted_repos[:5]
        ]

    def _activity_score(self, user: Dict, repos: list) -> int:
        score = 0
        if user.get('public_repos', 0) > 10: score += 20
        elif user.get('public_repos', 0) > 5: score += 10
        total_stars = sum(r.get('stargazers_count', 0) for r in repos)
        if total_stars > 50: score += 30
        elif total_stars > 10: score += 15
        if user.get('followers', 0) > 50: score += 20
        elif user.get('followers', 0) > 10: score += 10
        if len(repos) > 0:
            recent = sorted(repos, key=lambda r: r.get('updated_at', ''), reverse=True)
            if recent:
                score += 30
        return min(score, 100)

    def _compute_score(self, user: Dict, repos: list, activity: int) -> int:
        repo_score = min(user.get('public_repos', 0) * 2, 30)
        star_score = min(sum(r.get('stargazers_count', 0) for r in repos), 40)
        follower_score = min(user.get('followers', 0), 20)
        lang_score = min(len(set(r.get('language') for r in repos if r.get('language'))) * 2, 10)
        return min(repo_score + star_score + follower_score + lang_score + activity // 5, 100)
