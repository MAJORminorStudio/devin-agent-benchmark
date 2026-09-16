# Scrapy 3

Scrapy's redirect middleware mishandles a relative redirect response in the
downloader path. Reproduce the failure with the provided redirect test,
diagnose the URL/header handling, implement a focused fix that preserves
normal redirects, and run the relevant tests.
