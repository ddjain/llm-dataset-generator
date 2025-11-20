#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 <folder_path> [output_file]"
    exit 1
fi

FOLDER_PATH="$1"
OUTPUT_FILE="${2:-consolidated.jsonl}"

if [ ! -d "$FOLDER_PATH" ]; then
    echo "Error: Directory '$FOLDER_PATH' does not exist"
    exit 1
fi

> "$OUTPUT_FILE"

find "$FOLDER_PATH" -name "*.jsonl" -type f | while read -r file; do
    while IFS= read -r line; do
        if [ -n "$line" ]; then
            echo "$line" | jq --arg ref "$file" '. + {reference: $ref}' >> "$OUTPUT_FILE"
        fi
    done < "$file"
done

echo "Consolidated JSONL files into: $OUTPUT_FILE"
