from flask import Response
from lxml import html
import os

NO_RATE_LIMIT = os.getenv("NO_RATE_LIMIT", False)


# Add security headers to the response
def add_security_headers(response: Response):
    csp_policy = {
        "default-src": ["'self'"],
        "script-src": [
            "'self'",
            "https://code.jquery.com",
            "https://cdn.jsdelivr.net",
            "https://pagead2.googlesyndication.com",
            "cdn.datatables.net",
            "cdnjs.cloudflare.com",
            "www.googletagmanager.com",
            "partner.googleadservices.com",
            "tpc.googlesyndication.com",
        ],
        "style-src": [
            "'self'",
            "https://cdn.jsdelivr.net",
            "cdn.datatables.net",
            "fonts.googleapis.com",
        ],
        "img-src": [
            "'self'",
            "data:",
            "https://pagead2.googlesyndication.com",
            "https://saddlebagexchange.com",
        ],
        "font-src": [
            "'self'",
            "fonts.gstatic.com",
        ],
        "connect-src": [
            "'self'",
            "pagead2.googlesyndication.com",
            "www.google-analytics.com",
        ],
        "frame-src": [
            "'self'",
            "https://www.youtube.com",
            "googleads.g.doubleclick.net",
            "tpc.googlesyndication.com",
            "www.google.com",
        ],
    }
    csp_header_value = "; ".join(
        [f"{key} {' '.join(value)}" for key, value in csp_policy.items()]
    )
    response.headers["Content-Security-Policy"] = csp_header_value

    # Add other security headers
    response.headers["X-Frame-Options"] = "same-origin"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["X-XSS-Protection"] = "0"

    response.headers["Content-Security-Policy-Report-Only"] = (
        "default-src 'self'; script-src 'self' https://cdn.example.com; "
        "style-src 'self' https://cdn.example.com; img-src 'self' data: https://cdn.example.com;"
    )

    response.headers["Permissions-Policy"] = (
        "geolocation=(), camera=(), microphone=(), fullscreen=(), autoplay=(), payment=(), "
        "encrypted-media=(), midi=(), accelerometer=(), gyroscope=(), magnetometer=()"
    )
    return response


# Sanitize HTML content to prevent XSS
def return_safe_html(input_string):
    # disable for security testing
    if NO_RATE_LIMIT:
        return input_string
    document_root = html.fromstring(input_string)
    cleaned_html = html.tostring(document_root, pretty_print=True)
    # if `cleaned_html` differs from `input_string`, the input may contain malicious content.
    return cleaned_html
