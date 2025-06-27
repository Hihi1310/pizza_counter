#!/bin/bash
# Simple Pizza Counter Helper

show_usage() {
    echo "🍕 Pizza Counter Helper"
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup     - Create directories"
    echo "  zone      - Set up counting zone"
    echo "  build     - Build Docker image" 
    echo "  process   - Process video (place in input/ first)"
    echo "  batch     - Process all videos in input/"
    echo "  clean     - Clean output files"
    echo ""
}

case "$1" in
    setup)
        echo "Creating directories..."
        mkdir -p input output logs
        echo "✅ Done! Place videos in input/ folder"
        ;;
    zone)
        echo "Setting up counting zone..."
        python3 zone_setup.py
        ;;
    build)
        echo "Building Docker image..."
        docker-compose build
        echo "✅ Build complete!"
        ;;
    process)
        if [ -z "$(ls input/ 2>/dev/null)" ]; then
            echo "❌ No videos found in input/ directory"
            exit 1
        fi
        echo "Processing videos..."
        for video in input/*; do
            if [[ "$video" =~ \.(mp4|avi|mov|mkv)$ ]]; then
                echo "📹 Processing: $video"
                docker-compose run --rm pizza-counter python app.py \
                    --video "/app/$video" --save-video
            fi
        done
        echo "✅ Processing complete! Check output/ folder"
        ;;
    batch)
        echo "Starting batch processing..."
        docker-compose --profile batch up
        echo "✅ Batch complete! Check output/ folder"
        ;;
    clean)
        read -p "Delete all output files? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf output/* logs/*
            echo "✅ Cleaned up!"
        fi
        ;;
    *)
        show_usage
        ;;
esac
