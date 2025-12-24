#!/usr/bin/env python3
"""
GitHub Auto Commit Bot - REAL DATE VERSION
Uses Git commands with --date flag to create past date commits
Single File Solution
"""

import os
import sys
import json
import random
import time
import subprocess
import threading
from datetime import datetime, timedelta
import tempfile
import shutil
import math
from typing import List, Tuple, Dict

# ================= CONFIG =================
CONFIG_FILE = "github_real_dates.json"

def save_config(token, repos, git_name, git_email):
    config = {
        "github_token": token,
        "target_repos": repos,
        "git_name": git_name,
        "git_email": git_email,
        "last_setup": datetime.now().isoformat()
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return None, None, None, None
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        return (
            config.get("github_token"),
            config.get("target_repos", []),
            config.get("git_name"),
            config.get("git_email")
        )
    except:
        return None, None, None, None

# ================= GIT DATE COMMIT =================
class GitDateCommiter:
    def __init__(self, token, repos, git_name, git_email):
        self.token = token
        self.target_repos = repos
        self.git_name = git_name
        self.git_email = git_email
        self.commit_count = 0
        self.success_count = 0
        self.fail_count = 0
        self.running = False
        
        print(f"🔧 Git Commiter initialized")
        print(f"👤 Git User: {git_name} <{git_email}>")
        print(f"🎯 Target repos: {len(repos)}")
    
    def clone_repo(self, repo_url, temp_dir):
        """Clone repository to temporary directory"""
        try:
            # Clone with token authentication
            auth_url = repo_url.replace('https://', f'https://{self.token}@')
            cmd = ['git', 'clone', auth_url, temp_dir]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return True
            else:
                print(f"❌ Clone failed: {result.stderr[:100]}")
                return False
        except Exception as e:
            print(f"❌ Clone error: {e}")
            return False
    
    def make_date_commit(self, repo_url, commit_date, commit_message, content):
        """Make a commit with specific date using Git commands"""
        temp_dir = None
        try:
            # Create temp directory
            temp_dir = tempfile.mkdtemp(prefix='github_commit_')
            
            # Clone repo
            if not self.clone_repo(repo_url, temp_dir):
                return False
            
            # Change to repo directory
            os.chdir(temp_dir)
            
            # Configure git
            subprocess.run(['git', 'config', 'user.name', self.git_name], check=True)
            subprocess.run(['git', 'config', 'user.email', self.git_email], check=True)
            
            # Create file with content
            filename = f"commit_{commit_date.strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = os.path.join(temp_dir, filename)
            
            with open(filepath, 'w') as f:
                f.write(content)
            
            # Add file
            subprocess.run(['git', 'add', filename], check=True)
            
            # Format date for Git
            git_date = commit_date.strftime('%Y-%m-%d %H:%M:%S')
            
            # Commit with custom date
            env = os.environ.copy()
            env['GIT_AUTHOR_DATE'] = git_date
            env['GIT_COMMITTER_DATE'] = git_date
            
            commit_cmd = ['git', 'commit', '-m', commit_message]
            result = subprocess.run(
                commit_cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                print(f"⚠️  Commit failed: {result.stderr[:100]}")
                return False
            
            # Push to GitHub
            push_result = subprocess.run(
                ['git', 'push', 'origin', 'main'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if push_result.returncode == 0:
                self.commit_count += 1
                self.success_count += 1
                return True
            else:
                print(f"⚠️  Push failed: {push_result.stderr[:100]}")
                self.fail_count += 1
                return False
                
        except Exception as e:
            print(f"❌ Commit error: {e}")
            self.fail_count += 1
            return False
        finally:
            # Cleanup
            if temp_dir and os.path.exists(temp_dir):
                os.chdir('/')
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except:
                    pass
    
    def generate_repo_urls(self):
        """Generate repository URLs with token"""
        repo_urls = []
        for repo_name in self.target_repos:
            url = f"https://github.com/CodexNexor/{repo_name}.git"
            repo_urls.append(url)
        return repo_urls
    
    def humanize_365_days(self, start_date=None, min_commits=1, max_commits=8, activity_factor=0.7):
        """
        Create 365 days of commits with humanized pattern
        - Has gaps (not every day)
        - Variable commit count per day
        - More commits on weekdays, less on weekends
        - Occasional streaks and breaks
        """
        print(f"\n🌍 HUMANIZED 365 DAYS COMMIT PATTERN")
        print('='*60)
        print("🎯 Creating natural-looking contribution history")
        print("📊 Features:")
        print("  • Variable commit count (1-8 per day)")
        print("  • Weekday bias (more commits Monday-Friday)")
        print("  • Natural gaps (not every day)")
        print("  • Occasional streaks (3-7 days)")
        print("  • Occasional breaks (2-5 days)")
        print('='*60)
        
        if start_date is None:
            start_date = datetime.now() - timedelta(days=365)
        
        repo_urls = self.generate_repo_urls()
        if not repo_urls:
            print("❌ No repository URLs generated!")
            return 0
        
        total_made = 0
        self.running = True
        
        try:
            all_commits = []
            current_day = start_date
            
            # Generate pattern for 365 days
            for day_index in range(365):
                if not self.running:
                    break
                
                day_of_week = current_day.weekday()  # 0=Monday, 6=Sunday
                
                # Determine if we commit on this day (humanized probability)
                commit_probability = self._get_day_probability(day_of_week, activity_factor)
                
                # Roll the dice - sometimes skip even probable days
                if random.random() > commit_probability:
                    current_day += timedelta(days=1)
                    continue
                
                # Determine commit count for this day (humanized distribution)
                commit_count = self._get_commit_count(day_of_week, min_commits, max_commits)
                
                # Create commits for this day
                for commit_num in range(commit_count):
                    commit_time = self._get_commit_time(current_day, commit_num, commit_count)
                    
                    # Choose random repo
                    repo_url = random.choice(repo_urls)
                    
                    all_commits.append({
                        'date': commit_time,
                        'repo_url': repo_url,
                        'day_index': day_index,
                        'commit_num': commit_num,
                        'total_commits': commit_count
                    })
                
                current_day += timedelta(days=1)
            
            print(f"📅 Generated {len(all_commits)} commits across {len(set(c['day_index'] for c in all_commits))} active days")
            print(f"📊 Average: {len(all_commits)/365:.1f} commits/day")
            
            # Shuffle for natural distribution
            random.shuffle(all_commits)
            
            # Process commits
            start_time = time.time()
            for i, commit_data in enumerate(all_commits):
                if not self.running:
                    break
                
                commit_time = commit_data['date']
                repo_url = commit_data['repo_url']
                day_index = commit_data['day_index']
                commit_num = commit_data['commit_num']
                total_day_commits = commit_data['total_commits']
                
                # Create commit message and content
                commit_message = f"📅 Day {day_index+1}/365 - Commit {commit_num+1}/{total_day_commits}"
                content = f"""Humanized GitHub contribution
Date: {commit_time.strftime('%Y-%m-%d %H:%M:%S')}
Day: {day_index + 1} of 365
Commit: {commit_num + 1} of {total_day_commits}

This is part of a humanized 365-day contribution pattern.
Designed to look natural with variable frequency.
"""
                
                # Make commit with specific date
                success = self.make_date_commit(
                    repo_url,
                    commit_time,
                    commit_message,
                    content
                )
                
                if success:
                    total_made += 1
                
                # Show progress
                if (i + 1) % 10 == 0:
                    elapsed = time.time() - start_time
                    progress = ((i + 1) / len(all_commits)) * 100
                    speed = (i + 1) / max(elapsed, 1)
                    
                    print(f"📊 Progress: {i+1}/{len(all_commits)} ({progress:.1f}%)")
                    print(f"   ✅ Successful: {self.success_count}")
                    print(f"   ⏱️  Speed: {speed:.1f} commits/minute")
                    print(f"   📅 Date: {commit_time.strftime('%Y-%m-%d')}")
                    print(f"   🔗 Repo: {repo_url.split('/')[-1].replace('.git', '')}")
                    print()
                
                # Variable delay to look more human
                delay = random.uniform(1.5, 3.5)
                time.sleep(delay)
            
            elapsed = time.time() - start_time
            print(f"\n✅ HUMANIZED 365-DAYS COMPLETED!")
            print(f"📊 Total commits made: {total_made}")
            print(f"📅 Active days: {len(set(c['day_index'] for c in all_commits))}/365")
            print(f"⏱️  Time taken: {elapsed/60:.1f} minutes")
            print(f"✅ Successful: {self.success_count}")
            print(f"❌ Failed: {self.fail_count}")
            
            return total_made
            
        except KeyboardInterrupt:
            print(f"\n🛑 Interrupted")
            return total_made
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return total_made
    
    def _get_day_probability(self, day_of_week, activity_factor):
        """Get probability of committing on a given day"""
        # Base probabilities (more on weekdays)
        base_probabilities = {
            0: 0.85,  # Monday
            1: 0.90,  # Tuesday
            2: 0.88,  # Wednesday
            3: 0.87,  # Thursday
            4: 0.82,  # Friday
            5: 0.35,  # Saturday
            6: 0.25   # Sunday
        }
        
        # Apply activity factor
        prob = base_probabilities[day_of_week] * activity_factor
        
        # Add some randomness
        prob *= random.uniform(0.9, 1.1)
        
        return min(max(prob, 0), 1)
    
    def _get_commit_count(self, day_of_week, min_commits, max_commits):
        """Get commit count for a day based on day of week"""
        # Weighted distribution based on day
        day_weights = {
            0: 0.8,   # Monday - medium
            1: 1.0,   # Tuesday - high
            2: 0.9,   # Wednesday - high
            3: 0.85,  # Thursday - medium-high
            4: 0.7,   # Friday - medium
            5: 0.3,   # Saturday - low
            6: 0.2    # Sunday - very low
        }
        
        weight = day_weights[day_of_week]
        
        # Generate commit count with some randomness
        base_count = int(min_commits + (max_commits - min_commits) * weight)
        
        # Add randomness
        if random.random() < 0.3:  # 30% chance to be different
            variation = random.choice([-2, -1, 0, 1, 2])
            base_count += variation
        
        return max(min_commits, min(max_commits, base_count))
    
    def _get_commit_time(self, date, commit_num, total_commits):
        """Get commit time within a day"""
        # Distribute commits throughout the day
        if total_commits == 1:
            # Single commit around midday
            hour = random.randint(11, 15)
        else:
            # Multiple commits: spread them out
            # First commit later, last commit earlier
            if commit_num == 0:
                # First commit of the day
                hour = random.randint(9, 11)
            elif commit_num == total_commits - 1:
                # Last commit of the day
                hour = random.randint(16, 19)
            else:
                # Middle commits
                hour = random.randint(10, 17)
        
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        
        return date.replace(hour=hour, minute=minute, second=second)
    
    def fill_90_days_real(self, commits_per_day=3):
        """Fill 90 days with REAL date commits"""
        print(f"\n📅 FILLING 90 DAYS WITH REAL DATES")
        print('='*60)
        print(f"🎯 Target: {commits_per_day} commits/day for 90 days")
        print(f"📊 Total target: {90 * commits_per_day} commits")
        print('='*60)
        print("⚡ Using Git --date flag for real past dates...")
        print('='*60)
        
        self.running = True
        repo_urls = self.generate_repo_urls()
        
        if not repo_urls:
            print("❌ No repository URLs generated!")
            return 0
        
        total_made = 0
        start_time = time.time()
        
        try:
            # Generate all date-repo pairs
            today = datetime.now()
            all_commits = []
            
            for day_offset in range(90):
                target_date = today - timedelta(days=day_offset + 1)  # Start from yesterday
                
                for commit_num in range(commits_per_day):
                    # Random time during day (9 AM to 6 PM)
                    random_hour = random.randint(9, 18)
                    random_minute = random.randint(0, 59)
                    random_second = random.randint(0, 59)
                    
                    commit_time = target_date.replace(
                        hour=random_hour,
                        minute=random_minute,
                        second=random_second
                    )
                    
                    # Choose random repo
                    repo_url = random.choice(repo_urls)
                    
                    all_commits.append((commit_time, repo_url, commit_num))
            
            print(f"📅 Generated {len(all_commits)} commit plans")
            
            # Shuffle for natural distribution
            random.shuffle(all_commits)
            
            # Process commits
            for i, (commit_time, repo_url, commit_num) in enumerate(all_commits):
                if not self.running:
                    break
                
                # Create commit message and content
                commit_message = f"📅 Auto commit: {commit_time.strftime('%Y-%m-%d %H:%M')}"
                content = f"""Automated commit for GitHub contribution graph
Date: {commit_time.isoformat()}
Commit #{i+1}
Purpose: Fill contribution history

This commit was automatically generated to maintain
a consistent contribution history on GitHub.
"""
                
                # Make commit with specific date
                success = self.make_date_commit(
                    repo_url,
                    commit_time,
                    commit_message,
                    content
                )
                
                if success:
                    total_made += 1
                
                # Show progress
                if (i + 1) % 5 == 0:
                    elapsed = time.time() - start_time
                    speed = (i + 1) / max(elapsed, 1)
                    progress = ((i + 1) / len(all_commits)) * 100
                    
                    print(f"📊 Progress: {i+1}/{len(all_commits)} ({progress:.1f}%)")
                    print(f"   ✅ Successful: {self.success_count}")
                    print(f"   ⏱️  Speed: {speed:.1f} commits/minute")
                    print(f"   📅 Date: {commit_time.strftime('%Y-%m-%d')}")
                    print(f"   🔗 Repo: {repo_url.split('/')[-1].replace('.git', '')}")
                    print()
                
                # Delay to avoid rate limits
                time.sleep(2)
            
            elapsed = time.time() - start_time
            print(f"\n✅ 90-DAY FILL COMPLETED!")
            print(f"📊 Total commits made: {total_made}")
            print(f"⏱️  Time taken: {elapsed/60:.1f} minutes")
            print(f"✅ Successful: {self.success_count}")
            print(f"❌ Failed: {self.fail_count}")
            
            return total_made
            
        except KeyboardInterrupt:
            elapsed = time.time() - start_time
            print(f"\n🛑 Interrupted after {elapsed/60:.1f} minutes")
            print(f"📊 Made {total_made} commits")
            return total_made
        except Exception as e:
            print(f"❌ Error: {e}")
            return total_made
    
    def make_bulk_date_commits(self, total_commits=100, days_back=365):
        """Make bulk commits with random past dates"""
        print(f"\n⚡ BULK DATE COMMITS")
        print('='*60)
        print(f"🎯 Target: {total_commits} commits")
        print(f"📅 Date range: Last {days_back} days")
        print('='*60)
        
        self.running = True
        repo_urls = self.generate_repo_urls()
        
        if not repo_urls:
            print("❌ No repository URLs generated!")
            return 0
        
        total_made = 0
        start_time = time.time()
        
        try:
            for i in range(total_commits):
                if not self.running:
                    break
                
                # Generate random past date
                random_days = random.randint(1, days_back)
                commit_time = datetime.now() - timedelta(days=random_days)
                
                # Random time
                commit_time = commit_time.replace(
                    hour=random.randint(9, 18),
                    minute=random.randint(0, 59),
                    second=random.randint(0, 59)
                )
                
                # Choose repo
                repo_url = random.choice(repo_urls)
                
                # Create commit
                commit_message = f"📅 Past commit: {commit_time.strftime('%Y-%m-%d')}"
                content = f"""Automated past date commit
Date: {commit_time.isoformat()}
Commit #{i+1} of {total_commits}

Generated to fill GitHub contribution history.
"""
                
                success = self.make_date_commit(
                    repo_url,
                    commit_time,
                    commit_message,
                    content
                )
                
                if success:
                    total_made += 1
                
                # Show progress
                if (i + 1) % 10 == 0:
                    elapsed = time.time() - start_time
                    progress = ((i + 1) / total_commits) * 100
                    speed = (i + 1) / max(elapsed, 1)
                    
                    print(f"📊 Progress: {i+1}/{total_commits} ({progress:.1f}%)")
                    print(f"   ✅ Successful: {self.success_count}")
                    print(f"   ⏱️  Speed: {speed:.1f} commits/minute")
                    print(f"   📅 Last date: {commit_time.strftime('%Y-%m-%d')}")
                
                # Small delay
                time.sleep(1.5)
            
            elapsed = time.time() - start_time
            print(f"\n✅ BULK COMMITS COMPLETED!")
            print(f"📊 Made {total_made} commits with past dates")
            print(f"⏱️  Time: {elapsed/60:.1f} minutes")
            
            return total_made
            
        except KeyboardInterrupt:
            elapsed = time.time() - start_time
            print(f"\n🛑 Interrupted")
            print(f"📊 Made {total_made} commits")
            return total_made
    
    def create_streak(self, days=30, commits_per_day=3):
        """Create a streak of commits"""
        print(f"\n🔥 CREATING {days}-DAY STREAK")
        print('='*60)
        print(f"🎯 Target: {commits_per_day} commits/day for {days} days")
        print(f"📊 Total: {days * commits_per_day} commits")
        print('='*60)
        
        self.running = True
        repo_urls = self.generate_repo_urls()
        
        if not repo_urls:
            print("❌ No repository URLs generated!")
            return 0
        
        total_made = 0
        start_time = time.time()
        
        try:
            today = datetime.now()
            
            for day_offset in range(days):
                if not self.running:
                    break
                
                # Date for this day (starting from yesterday going backwards)
                commit_date = today - timedelta(days=day_offset + 1)
                
                print(f"\n📅 Day {day_offset + 1}/{days}: {commit_date.strftime('%Y-%m-%d')}")
                print('-' * 40)
                
                day_commits = 0
                
                for commit_num in range(commits_per_day):
                    # Random time during day
                    commit_time = commit_date.replace(
                        hour=random.randint(9, 18),
                        minute=random.randint(0, 59),
                        second=random.randint(0, 59)
                    )
                    
                    # Choose repo
                    repo_url = repo_urls[day_offset % len(repo_urls)]
                    
                    # Create commit
                    commit_message = f"🔥 Day {day_offset + 1}, Commit {commit_num + 1}"
                    content = f"""Streak building commit
Date: {commit_time.isoformat()}
Streak day: {day_offset + 1}/{days}
Commit: {commit_num + 1}/{commits_per_day}

Building GitHub contribution streak.
"""
                    
                    success = self.make_date_commit(
                        repo_url,
                        commit_time,
                        commit_message,
                        content
                    )
                    
                    if success:
                        total_made += 1
                        day_commits += 1
                    
                    # Small delay between commits
                    time.sleep(1)
                
                print(f"   ✅ Day completed: {day_commits} commits")
                
                # Delay between days
                if day_offset < days - 1:
                    time.sleep(2)
            
            elapsed = time.time() - start_time
            print(f"\n🎉 STREAK CREATED!")
            print(f"📊 Total commits: {total_made}")
            print(f"📅 Streak length: {days} days")
            print(f"⏱️  Time: {elapsed/60:.1f} minutes")
            
            return total_made
            
        except KeyboardInterrupt:
            elapsed = time.time() - start_time
            print(f"\n🛑 Streak interrupted")
            print(f"📊 Made {total_made} commits")
            return total_made

# ================= CLI =================
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    banner = """
╔══════════════════════════════════════════════════╗
║        🚀 GITHUB AUTO COMMIT BOT 🚀              ║
║         REAL DATE COMMITS EDITION                ║
╚══════════════════════════════════════════════════╝
"""
    print(banner)

def print_menu():
    print("\n" + "="*50)
    print("📋 REAL DATE MENU")
    print("="*50)
    print("1. 📅 Fill 90 Days (REAL dates - Git --date flag)")
    print("2. 🌍 Humanized 365 Days (Natural pattern)")
    print("3. ⚡ Bulk Past Commits (Random dates)")
    print("4. 🔥 Create Custom Streak")
    print("5. 📊 View statistics")
    print("6. 🎯 Change target repos")
    print("7. 👤 Change Git user info")
    print("8. 🔧 Test Git installation")
    print("9. ❌ Exit")
    print("="*50)

def get_github_token():
    print("\n" + "="*60)
    print("🔑 GITHUB TOKEN SETUP")
    print("="*60)
    
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        print("✅ Found token in environment")
        use_env = input("Use environment token? (y/n): ").lower()
        if use_env == 'y':
            return token
    
    print("\n📋 Paste GitHub token (requires 'repo' scope): ")
    token = input("Token: ").strip()
    return token

def get_git_user_info():
    print("\n" + "="*60)
    print("👤 GIT USER INFORMATION")
    print("="*60)
    print("This will be used for commit authorship")
    print("="*60)
    
    # Try to get from git config
    try:
        name_result = subprocess.run(
            ['git', 'config', 'user.name'],
            capture_output=True,
            text=True
        )
        email_result = subprocess.run(
            ['git', 'config', 'user.email'],
            capture_output=True,
            text=True
        )
        
        git_name = name_result.stdout.strip() if name_result.returncode == 0 else ""
        git_email = email_result.stdout.strip() if email_result.returncode == 0 else ""
        
        if git_name and git_email:
            print(f"✅ Found Git config: {git_name} <{git_email}>")
            use_current = input("Use current Git config? (y/n): ").lower()
            if use_current == 'y':
                return git_name, git_email
    except:
        pass
    
    # Get from user
    print("\nEnter Git user information:")
    git_name = input("Your name (for commits): ").strip()
    git_email = input("Your email (for commits): ").strip()
    
    return git_name, git_email

def get_target_repos():
    print("\n" + "="*60)
    print("🎯 ENTER REPOSITORY NAMES")
    print("="*60)
    print("Enter repository names (without URL)")
    print("Example: 'my-project', 'learning-python'")
    print("="*60)
    
    repos = []
    print("\nEnter repository names (one per line, empty to finish):")
    
    i = 1
    while True:
        name = input(f"Repo {i}: ").strip()
        if not name:
            if repos:
                break
            print("❌ Need at least 1 repository")
            continue
        repos.append(name)
        i += 1
    
    print(f"\n✅ Target repos ({len(repos)}):")
    for i, repo in enumerate(repos, 1):
        print(f"  {i}. {repo}")
    
    return repos

def get_number(prompt, default, min_val, max_val):
    while True:
        try:
            value = input(f"{prompt} [{default}]: ").strip()
            if not value:
                value = default
            else:
                value = int(value)
            
            if min_val <= value <= max_val:
                return value
            print(f"❌ Must be between {min_val} and {max_val}")
        except ValueError:
            print("❌ Please enter a number")

def test_git_installation():
    print("\n🔧 TESTING GIT INSTALLATION")
    print("="*40)
    
    try:
        # Test git command
        result = subprocess.run(
            ['git', '--version'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Git installed: {result.stdout.strip()}")
        else:
            print("❌ Git not found or not working")
            print("💡 Install Git from: https://git-scm.com/downloads")
            return False
        
        # Test git config
        name_result = subprocess.run(
            ['git', 'config', 'user.name'],
            capture_output=True,
            text=True
        )
        email_result = subprocess.run(
            ['git', 'config', 'user.email'],
            capture_output=True,
            text=True
        )
        
        if name_result.returncode == 0:
            print(f"✅ Git user: {name_result.stdout.strip()}")
        else:
            print("⚠️  Git user.name not set")
        
        if email_result.returncode == 0:
            print(f"✅ Git email: {email_result.stdout.strip()}")
        else:
            print("⚠️  Git user.email not set")
        
        return True
        
    except Exception as e:
        print(f"❌ Git test error: {e}")
        return False

def main():
    clear_screen()
    print_banner()
    
    # Test Git installation
    if not test_git_installation():
        print("\n❌ Git is required for real date commits")
        print("💡 Install Git first: https://git-scm.com/downloads")
        input("Press Enter to exit...")
        return
    
    # Load or create config
    token, repos, git_name, git_email = load_config()
    
    if not token or not repos or not git_name or not git_email:
        print("\n🔧 First-time setup\n")
        
        if not token:
            token = get_github_token()
            if not token:
                print("❌ Token required. Exiting...")
                return
        
        if not git_name or not git_email:
            git_name, git_email = get_git_user_info()
        
        if not repos:
            repos = get_target_repos()
        
        save_config(token, repos, git_name, git_email)
        print(f"\n✅ Configuration saved!")
        time.sleep(1)
    else:
        print(f"✅ Loaded configuration")
        print(f"👤 Git User: {git_name} <{git_email}>")
        print(f"🎯 Repos: {', '.join(repos[:3])}{'...' if len(repos) > 3 else ''}")
        time.sleep(1)
    
    # Create commiter
    commiter = GitDateCommiter(token, repos, git_name, git_email)
    
    # Main loop
    while True:
        clear_screen()
        print_banner()
        print(f"\n👤 Git User: {git_name}")
        print(f"📧 Git Email: {git_email}")
        print(f"🎯 Repos: {len(repos)} repositories")
        print(f"✅ Total Commits: {commiter.commit_count}")
        print(f"✅ Successful: {commiter.success_count}")
        print(f"❌ Failed: {commiter.fail_count}")
        
        print_menu()
        
        try:
            choice = input("\n🎯 Choice (1-9): ").strip()
            
            if choice == '1':
                print("\n" + "="*60)
                print("📅 FILL 90 DAYS WITH REAL DATES")
                print("="*60)
                print("This will:")
                print("1. Clone your repositories")
                print("2. Make commits with past dates")
                print("3. Push to GitHub")
                print("4. Create 90 days of green squares!")
                print("="*60)
                
                commits_per_day = get_number("Commits per day (1-10)", 3, 1, 10)
                confirm = input(f"\nCreate {commits_per_day} commits/day for 90 days? (y/n): ").lower()
                
                if confirm == 'y':
                    print("\n⚠️  This will take 15-30 minutes")
                    print("   Each commit uses Git with --date flag")
                    print("   Your GitHub graph will be COMPLETELY GREEN")
                    print("="*60)
                    
                    final_confirm = input("\nStart 90-day fill? (y/n): ").lower()
                    if final_confirm == 'y':
                        commiter.fill_90_days_real(commits_per_day)
                
                input("\nPress Enter...")
            
            elif choice == '2':
                print("\n" + "="*60)
                print("🌍 HUMANIZED 365 DAYS")
                print("="*60)
                print("Create natural-looking commit history:")
                print("• Not every day (human-like gaps)")
                print("• More commits on weekdays")
                print("• Fewer commits on weekends")
                print("• Variable commit counts")
                print("="*60)
                
                min_commits = get_number("Minimum commits per day (1-5)", 1, 1, 5)
                max_commits = get_number("Maximum commits per day (3-15)", 8, 3, 15)
                activity_factor = get_number("Activity level (50-100%)", 70, 50, 100) / 100
                
                print(f"\n📊 Expected pattern:")
                print(f"   • Min commits/day: {min_commits}")
                print(f"   • Max commits/day: {max_commits}")
                print(f"   • Activity level: {activity_factor*100:.0f}%")
                print(f"   • Approx total: ~{int(365 * (min_commits+max_commits)/2 * activity_factor)} commits")
                print("="*60)
                
                confirm = input("\nCreate humanized 365-day history? (y/n): ").lower()
                if confirm == 'y':
                    print("\n⚠️  This will take 60-90 minutes")
                    print("   Creating natural-looking contribution graph")
                    print("   With gaps and variable intensity")
                    print("="*60)
                    
                    final_confirm = input("\nStart 365-day humanized pattern? (y/n): ").lower()
                    if final_confirm == 'y':
                        # Start from 365 days ago
                        start_date = datetime.now() - timedelta(days=365)
                        commiter.humanize_365_days(start_date, min_commits, max_commits, activity_factor)
                
                input("\nPress Enter...")
            
            elif choice == '3':
                print("\n" + "="*60)
                print("⚡ BULK PAST DATE COMMITS")
                print("="*60)
                
                total_commits = get_number("How many commits? (1-500)", 100, 1, 500)
                days_back = get_number("How many days back? (1-365)", 365, 1, 365)
                
                confirm = input(f"\nCreate {total_commits} commits with random past dates? (y/n): ").lower()
                if confirm == 'y':
                    commiter.make_bulk_date_commits(total_commits, days_back)
                
                input("\nPress Enter...")
            
            elif choice == '4':
                print("\n" + "="*60)
                print("🔥 CREATE CUSTOM STREAK")
                print("="*60)
                
                days = get_number("Streak length in days (1-365)", 30, 1, 365)
                commits_per_day = get_number("Commits per day (1-10)", 3, 1, 10)
                
                total = days * commits_per_day
                confirm = input(f"\nCreate {days}-day streak with {total} total commits? (y/n): ").lower()
                
                if confirm == 'y':
                    commiter.create_streak(days, commits_per_day)
                
                input("\nPress Enter...")
            
            elif choice == '5':
                print(f"\n📊 STATISTICS")
                print("="*40)
                print(f"✅ Total Commits: {commiter.commit_count}")
                print(f"✅ Successful: {commiter.success_count}")
                print(f"❌ Failed: {commiter.fail_count}")
                print(f"🎯 Target Repos: {len(repos)}")
                print(f"🏃‍♂️ Status: {'Running' if commiter.running else 'Stopped'}")
                
                if commiter.commit_count > 0:
                    success_rate = (commiter.success_count / commiter.commit_count) * 100
                    print(f"📈 Success Rate: {success_rate:.1f}%")
                    
                    print(f"\n📅 GitHub Graph Estimate:")
                    estimated_days = min(365, commiter.success_count // 3)
                    print(f"  • Green days: ~{estimated_days}")
                    print(f"  • Total commits: {commiter.success_count}")
                    
                    if estimated_days >= 365:
                        print(f"  • Status: 🌍 Full year streak!")
                    elif estimated_days >= 100:
                        print(f"  • Status: 🔥 {estimated_days}-day streak!")
                    elif estimated_days >= 30:
                        print(f"  • Status: ⭐ {estimated_days}-day streak")
                    else:
                        print(f"  • Status: 📈 Building...")
                
                input("\nPress Enter...")
            
            elif choice == '6':
                new_repos = get_target_repos()
                repos = new_repos
                save_config(token, repos, git_name, git_email)
                commiter.target_repos = repos
                print(f"\n✅ Repositories updated!")
                input("\nPress Enter...")
            
            elif choice == '7':
                new_name, new_email = get_git_user_info()
                git_name, git_email = new_name, new_email
                save_config(token, repos, git_name, git_email)
                commiter.git_name = git_name
                commiter.git_email = git_email
                print(f"\n✅ Git user info updated!")
                input("\nPress Enter...")
            
            elif choice == '8':
                test_git_installation()
                input("\nPress Enter...")
            
            elif choice == '9':
                commiter.running = False
                print("\n👋 Goodbye!")
                time.sleep(1)
                break
            
            else:
                print("❌ Invalid choice")
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping...")
            commiter.running = False
            time.sleep(1)
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(2)

# ================= ENTRY POINT =================
if __name__ == "__main__":
    # Check for Git
    try:
        subprocess.run(['git', '--version'], capture_output=True)
    except:
        print("❌ Git is not installed or not in PATH")
        print("💡 Download Git from: https://git-scm.com/downloads")
        print("💡 After installing, restart your terminal")
        input("Press Enter to exit...")
        sys.exit(1)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Exiting...")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")