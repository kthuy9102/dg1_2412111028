#!/bin/bash

if [ $# -ne 1 ] || [ ! -d "$1" ]; then
    echo "Loi: Vui long cung cap mot thu muc hop le."
    exit 1
fi

TARGET_DIR="$1"
DIR_NAME=$(basename "$TARGET_DIR")
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="$HOME/backup"

mkdir -p "$BACKUP_DIR"
DEST_FILE="$BACKUP_DIR/${DIR_NAME}_${TIMESTAMP}.tar.gz"

tar -czf "$DEST_FILE" -C "$(dirname "$TARGET_DIR")" "$DIR_NAME"

echo "[$(date +"%Y-%m-%d %H:%M:%S")] Backed up $TARGET_DIR to $DEST_FILE" >> logs/backup.log

echo "Sao luu thanh cong: $DEST_FILE"
