# Customer Service Agent - Git Preparation

This document outlines the steps to prepare and push your project to GitHub.

## 1. Verify `.gitignore`
Make sure `.gitignore` exists and excludes sensitive files:
- `.env` (contains API keys!)
- `*_data/` (database storage)
- `__pycache__`
- `venv/` or `.venv/`

## 2. Initialize Git (if not already done)
```bash
git init
git add .
git status
```

> **Check `git status` output carefully!** Ensure `qdrant_data`, `neo4j_data`, etc. are NOT listed.

## 3. Commit Changes
```bash
git commit -m "Initial commit: Customer Service Agent with LightRAG + Neo4j"
```

## 4. Rename Branch to Main
```bash
git branch -M main
```

## 5. Add Remote and Push
Replace `<your-repo-url>` with your actual GitHub repository URL.

```bash
git remote add origin <your-repo-url>
git push -u origin main
```

## ⚠️ Important Security Note
**NEVER** commit your `.env` file. We have already added it to `.gitignore`.
If you accidentally committed it, you must remove it from history or rotate all your API keys immediately.
