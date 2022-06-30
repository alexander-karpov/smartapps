/usr/bin/python3.10 -m uvicorn server:app \
    --host 0.0.0.0 \
    --port 5000 \
    --workers 1 \
    --no-access-log
