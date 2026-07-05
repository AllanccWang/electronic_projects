#!/bin/bash

echo "## 🔧 Project Index (Sorted by LAB Number)" > index.md

# Sort folders by LAB number using version-aware sort
for dir in $(ls -d LAB*/ | sort -V); do
  # Remove trailing slash for cleaner link text
  clean_name="${dir%/}"
  echo "- [$clean_name/]($clean_name/)" >> index.md
done
