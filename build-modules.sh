#!/bin/bash
# Bio-Finder Module Builder Script for Automated Environments
# Usage: ./build-modules.sh [tool1] [tool2] [tool3] ...

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIOFINDER="$SCRIPT_DIR/biofinder"

# Check if bio-finder exists
if [[ ! -x "$BIOFINDER" ]]; then
    echo "Error: biofinder not found at $BIOFINDER"
    exit 1
fi

build_module() {
    local tool="$1"
    echo "Building module for: $tool"
    
    # Use the command we know works from testing
    if sudo -E env "PATH=$PATH" "$BIOFINDER" build "$tool"; then
        echo "✓ Successfully built module for $tool"
        return 0
    else
        echo "✗ Failed to build module for $tool" 
        return 1
    fi
}

# If no arguments provided, show usage
if [[ $# -eq 0 ]]; then
    echo "Bio-Finder Module Builder for Automated Environments"
    echo ""
    echo "Usage: ./build-modules.sh [tool1] [tool2] [tool3] ..."
    echo ""
    echo "Examples:"
    echo "  ./build-modules.sh samtools"
    echo "  ./build-modules.sh samtools fastqc bowtie2"
    echo "  ./build-modules.sh samtools/1.22--h96c455f_0"
    echo ""
    echo "This script will:"
    echo "  - Build Lmod module files in /apps/Modules/modulefiles/"
    echo "  - Use the latest version if no version specified"
    echo "  - Handle sudo permissions automatically"
    echo "  - Preserve Python environment for MCP dependencies"
    exit 0
fi

echo "=== Bio-Finder Automated Module Builder ==="
echo "Building modules for: $*"
echo ""

# Build modules for each tool specified
success_count=0
total_count=$#

for tool in "$@"; do
    if build_module "$tool"; then
        success_count=$((success_count + 1))
    fi
    echo ""
done

echo "=== Results ==="
echo "Successfully built: $success_count/$total_count modules"

if [[ $success_count -eq $total_count ]]; then
    echo "🎉 All modules built successfully!"
    echo ""
    echo "To see available modules: module avail"
    echo "To load a module: module load <tool>/<version>"
else
    echo "⚠️ Some modules failed to build"
    exit 1
fi