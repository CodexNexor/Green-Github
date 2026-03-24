# GitHub Auto Commit Bot (Real Date Edition)

This project helps you **fill your GitHub contribution graph with green squares** by creating commits with **real past dates** using Git’s `--date` mechanism.

> ⚠️ **Disclaimer**  
> This tool is provided for educational, testing, and personal experimentation purposes only.  
> Misuse may violate GitHub’s terms or misrepresent activity. Use responsibly.

---

## ✨ Features

- ✅ Real Git commits (no API spoofing)
- 📅 Commits with **real past dates**
- 🌍 Humanized 365-day contribution history
- 🔥 Custom streak creation
- ⚡ Bulk random past commits
- 🧠 Randomized commit times & messages
- 🗂 Supports multiple repositories
- 🧹 Temporary clone & automatic cleanup

---

## 🧰 Requirements

- **Python 3.8+**
- **Git**
- **GitHub Personal Access Token** with `repo` scope

Verify Git installation:

```bash
git --version

📦 Installation

Clone the repository:

git clone https://github.com/your-username/your-repo.git
cd your-repo


(Optional – Linux/macOS)

chmod +x github_commit.py

🔑 GitHub Token Setup

Create a GitHub Personal Access Token:

GitHub → Settings

Developer Settings

Personal Access Tokens

Generate token with:

✅ repo scope

Option 1: Set as Environment Variable

Linux / macOS

export GITHUB_TOKEN=your_token_here


Windows (PowerShell)

setx GITHUB_TOKEN "your_token_here"

Option 2: Paste when prompted

The script will ask for the token on first run.

🏁 First-Time Setup

On first launch, the script will request:

GitHub token

Git commit author name

Git commit author email

Target repository names (must already exist)

Configuration is saved locally in:

github_real_dates.json

▶️ How to Run

Start the program:

python github_commit.py


You’ll be presented with an interactive CLI menu.

📋 Menu Options Explained
1️⃣ Fill 90 Days (Real Dates)

Creates commits for the last 90 days

Uses Git real date flags

Ideal for fast graph filling

Recommended: 2–4 commits/day

2️⃣ Humanized 365 Days (Natural Pattern)

Creates a realistic GitHub history:

Not every day has commits

Weekday-heavy activity

Weekend drops

Random streaks and breaks

Variable commit counts

Best for a natural-looking contribution graph.

3️⃣ Bulk Past Commits

Generates random commits across past dates

Choose:

Total commits

Days back range

4️⃣ Create Custom Streak

Build a continuous streak

Choose:

Streak length (days)

Commits per day

5️⃣ View Statistics

Displays:

Total commits

Successful vs failed

Estimated green days

Success rate

6️⃣ Change Target Repositories

Update repository list without restarting setup.

7️⃣ Change Git User Info

Modify commit author name and email.

8️⃣ Test Git Installation

Checks:

Git availability

Git user configuration

9️⃣ Exit

Safely stops the program.

⚙️ How It Works (Technical Overview)

Clones target repository into a temporary directory

Creates a unique file per commit

Uses environment variables:

GIT_AUTHOR_DATE

GIT_COMMITTER_DATE

Commits and pushes to main

Automatically deletes temp directories

⚠️ Important Notes

Repositories must already exist

Default branch assumed: main

Large runs may take 30–90 minutes

GitHub may delay graph updates (up to 24h)

📜 License

MIT License. Use at your own risk.
