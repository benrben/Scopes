#!/bin/bash
# Quick reference: alias to use scopes CLI from anywhere

alias scopes="python3 /Users/benreich/Scopes/scopes/cli.py"

# Common commands to get started:

# See all scopes
# scopes scopes

# Find by intent
# scopes locate --intent "add authentication"

# Read a scope
# scopes read scope="Auth/Login"

# Read code snippets from evidence
# scopes read:code scope="Auth/Login" --section "Entry Points"

# Search across all scopes
# scopes search --query "token validation"

# Start a work session
# scopes session:start --scope "Auth" --goal "Implement TOTP"

# Create a task
# scopes task:create --scope "Auth" --title "Add rate limiting"

# Check project health
# scopes status
# scopes orphans
# scopes unresolved

# List agents and skills
# scopes agents
# scopes skills

# Initialize a new Scopes project
# scopes init

# Get help
# scopes help
# scopes version
