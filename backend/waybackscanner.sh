#!/bin/bash

# Check if domain was passed
if [ -z "$1" ]; then
    echo "Usage: $0 https://example.com"
    exit 1
fi

DOMAIN=$1

if [[ "$DOMAIN" == http*://* ]]; then
    OUTDOMAIN=${DOMAIN#*://}
else
    OUTDOMAIN=$DOMAIN
fi

# Output directories
OUTPUT_DIR="/home/wolf/Desktop/code/ScanXpert/backend/reports/$OUTDOMAIN"
mkdir -p "$OUTPUT_DIR"

# Temporary files
ALL_TMP="$OUTPUT_DIR/all.txt"
UNIQUE_TMP="$OUTPUT_DIR/unique.txt"
WAYBACK_OUT="$OUTPUT_DIR/waybackurls.txt"

# Step 1: Extract URLs
echo "[*] Running katana on $DOMAIN..."
katana -u "$DOMAIN" -silent > "$ALL_TMP"

# Step 2: Filter unique URLs
echo "[*] Filtering with uro..."
cat "$ALL_TMP" | uro > "$UNIQUE_TMP"

# Step 3: Check HTTP status and titles
echo "[*] Running httpx..."
cat "$UNIQUE_TMP" | httpx -silent -sc -title -nc -mc 200,403,302 > "$WAYBACK_OUT"

# Step 4: Run GF filters
echo "[*] Running GF patterns..."
cat "$WAYBACK_OUT" | gf xss > "$OUTPUT_DIR/xss.txt"
cat "$WAYBACK_OUT" | gf sqli > "$OUTPUT_DIR/sqli.txt"
cat "$WAYBACK_OUT" | gf lfi > "$OUTPUT_DIR/lfi.txt"
cat "$WAYBACK_OUT" | grep '.js' > "$OUTPUT_DIR/js.txt"
cat "$WAYBACK_OUT" | gf ssrf > "$OUTPUT_DIR/ssrf.txt"

echo "[+] Done. Results saved in $OUTPUT_DIR"
