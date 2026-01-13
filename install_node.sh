#!/bin/bash
# Script to install Node.js and pnpm

# Load nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Install Node.js LTS
echo "Installing Node.js LTS..."
nvm install --lts
nvm use --lts
nvm alias default lts/*

# Verify Node.js installation
echo "Node.js version:"
node --version
echo "npm version:"
npm --version

# Install pnpm
echo "Installing pnpm..."
npm install -g pnpm

# Verify pnpm installation
echo "pnpm version:"
pnpm --version

echo "✅ Node.js and pnpm installation complete!"
