uvicorn \
    --reload server:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --reload-dir ./smartapps \
    --reload-delay 1 \
    --workers 1 \
    --no-access-log
