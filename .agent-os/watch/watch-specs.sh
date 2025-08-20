#!/bin/bash

# Hotel Onboarding System - Specification Watcher
# This script watches for new specifications and triggers Claude Code

# Configuration
SPEC_DIR="/users/gouthamvemula/onbclaude/onbdev-demo/.agent-os/specs"
IMPL_DIR="/users/gouthamvemula/onbclaude/onbdev-demo/.agent-os/implementations"
REVIEW_DIR="/users/gouthamvemula/onbclaude/onbdev-demo/.agent-os/reviews"
LOG_FILE="/users/gouthamvemula/onbclaude/onbdev-demo/.agent-os/watch/watch.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create directories if they don't exist
mkdir -p "$IMPL_DIR"
mkdir -p "$REVIEW_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

echo -e "${GREEN}🚀 Hotel Onboarding System - Specification Watcher${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "📁 Watching: $SPEC_DIR"
echo "🔧 Implementations: $IMPL_DIR"
echo "📝 Reviews: $REVIEW_DIR"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Function to process new spec
process_spec() {
    local spec_path="$1"
    local spec_name=$(basename "$spec_path")
    local impl_path="$IMPL_DIR/$spec_name"
    local review_path="$REVIEW_DIR/$spec_name"
    
    echo -e "\n${YELLOW}📋 New specification detected: $spec_name${NC}"
    log_message "Processing specification: $spec_name"
    
    # Check if already processed
    if [ -f "$spec_path/status.json" ]; then
        status=$(grep -o '"status"[[:space:]]*:[[:space:]]*"[^"]*"' "$spec_path/status.json" | cut -d'"' -f4)
        if [ "$status" = "completed" ]; then
            echo -e "${GREEN}✅ Already completed, skipping${NC}"
            return
        fi
        if [ "$status" = "processing" ]; then
            echo -e "${YELLOW}⏳ Currently processing, skipping${NC}"
            return
        fi
    fi
    
    # Create implementation directory structure
    mkdir -p "$impl_path/files"
    mkdir -p "$impl_path/tests"
    mkdir -p "$review_path"
    
    # Update status to processing
    echo '{"status": "processing", "started_at": "'$(date -Iseconds)'"}' > "$spec_path/status.json"
    
    # Create implementation request file for Claude Code
    cat > "$impl_path/request.md" << EOF
# Implementation Request: $spec_name

## Project Context
- **Project Path:** /users/gouthamvemula/onbclaude/onbdev-demo
- **Backend:** hotel-onboarding-backend/
- **Frontend:** hotel-onboarding-frontend/
- **Follow:** CLAUDE.md guidelines

## Specification
$(cat "$spec_path/spec.md" 2>/dev/null || echo "No spec.md found")

## Tasks to Complete
$(cat "$spec_path/tasks.md" 2>/dev/null || echo "No tasks.md found")

## Output Requirements
1. Write implementation files to: $impl_path/files/
2. Write test files to: $impl_path/tests/
3. Follow existing patterns in the codebase
4. Ensure property isolation is maintained
5. Add appropriate error handling

## Current System Status
- Backend: FastAPI with Supabase
- Frontend: React + TypeScript + Vite
- Most onboarding steps are implemented
- Focus