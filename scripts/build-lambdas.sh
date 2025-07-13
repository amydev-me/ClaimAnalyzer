#!/bin/bash
set -e

echo "🔨 Building Lambda functions..."

# Create artifacts directory
mkdir -p artifacts

# Function to build a Lambda function
build_lambda() {
    local function_name=\$1
    local source_dir=\$2
    
    echo "Building ${function_name}..."
    
    # Create temporary build directory
    BUILD_DIR=$(mktemp -d)
    
    # Copy source files
    cp -r ${source_dir}/* ${BUILD_DIR}/
    
    # Install dependencies if requirements.txt exists
    if [ -f "${source_dir}/requirements.txt" ]; then
        echo "Installing dependencies for ${function_name}..."
        pip install -r ${source_dir}/requirements.txt -t ${BUILD_DIR}/
    fi
    
    # Create zip file
    cd ${BUILD_DIR}
    zip -r $(pwd)/../../artifacts/${function_name}.zip .
    cd - > /dev/null
    
    # Cleanup
    rm -rf ${BUILD_DIR}
    
    echo "✅ ${function_name}.zip created"
}

# Build each Lambda function
build_lambda "upload_handler" "lambda"
build_lambda "submission_analyzer" "lambda"

echo "📋 Artifacts created:"
ls -la artifacts/

echo "🎉 Build completed!"