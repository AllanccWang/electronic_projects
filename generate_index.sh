#!/bin/bash

echo "## 🔧 Project Index (Sorted by LAB Number)" > index.md

# Sort folders by LAB number without splitting names that contain spaces
while IFS= read -r -d '' dir; do
  # Remove trailing slash for cleaner link text
  clean_name="${dir%/}"
  link_name="${clean_name// /%20}"
  printf '%s\n' "- [$clean_name/]($link_name/)" >> index.md
done < <(printf '%s\0' LAB*/ | sort -zV)
