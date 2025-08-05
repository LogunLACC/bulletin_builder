# This script searches for a specific text pattern within all Python files
# in the current directory and its subdirectories.

# --- Configuration ---
# The function name or text you want to find.
$SearchTerm = "open_template_gallery"
# The type of files to search in (e.g., '*.py' for Python).
$FilePattern = "*.py"
# The directory to start the search from ('.' means the current directory).
$SearchDir = "."

# --- Script Logic ---
Write-Host "Searching for '$SearchTerm' in all $FilePattern files..."
Write-Host "--------------------------------------------------"

# Use Get-ChildItem to find files and pipe them to Select-String to search their content.
# -Recurse: Search in subdirectories.
# -Filter: Specifies the file pattern.
# Select-Object -Unique Path: Displays only the path of each matching file, without duplicates.
$Results = Get-ChildItem -Path $SearchDir -Recurse -Filter $FilePattern | Select-String -Pattern $SearchTerm | Select-Object -Unique Path

# --- Display Results ---
if ($null -eq $Results) {
  Write-Host "No files found containing '$SearchTerm'."
} else {
  Write-Host "Found the search term in the following file(s):"
  # The output from the command is a list of objects, so we loop through them.
  $Results | ForEach-Object { $_.Path }
}

Write-Host "--------------------------------------------------"
Write-Host "Search complete."
