FROM python:3.11-slim@sha256:6c5ae9d998f4cc06f892f428d7af53a566c24ad0dc29fa572696b647cf2762a7

COPY allowlist_proxy.py /allowlist_proxy.py

EXPOSE 3128

ENTRYPOINT ["python3", "/allowlist_proxy.py"]
