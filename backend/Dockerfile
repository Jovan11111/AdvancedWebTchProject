FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p /app/instance /app/static/book-covers
RUN mkdir -p /app/default-covers && cp /app/static/book-covers/placeholder_book_cover.jpeg /app/default-covers/placeholder_book_cover.jpeg

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]