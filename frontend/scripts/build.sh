#!/bin/bash

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

current_dir="$PWD"

cd /home/ghf/workspace/external-cockpit/frontend/cockpit

npm install
npm run build