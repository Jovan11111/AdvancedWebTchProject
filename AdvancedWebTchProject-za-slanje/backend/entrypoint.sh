#!/bin/sh
set -e

mkdir -p /app/static/book-covers /data
if [ ! -f /app/static/book-covers/placeholder_book_cover.jpeg ]; then
    cp /app/default-covers/placeholder_book_cover.jpeg /app/static/book-covers/placeholder_book_cover.jpeg
fi

exec gunicorn --bind 0.0.0.0:5000 --workers 1 app:app