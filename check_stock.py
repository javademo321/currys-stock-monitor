#!/usr/bin/env python3
"""
Currys Business stock monitor.

Checks whether a specific product is back in stock and, if so, sends an email
alert via Web3Forms (https://web3forms.com) — a free form-to-email service that
needs no SMTP server or password, just an access key.

Designed to run on GitHub Actions (see .github/workflows/stock-check.yml) but
works anywhere Python 3 + `requests` is available.

Environment variables:
  WEB3FORMS_KEY  (required to send email) - your Web3Forms access key.
"""

import os
import sys
import requests

# --- What we are watching -----------------------------------------------------
PRODUCT_NAME = 'APPLE MacBook Pro 16" (2026) - M5 Max, 2 TB SSD, RAM 48 GB, Space Black'
PRODUCT_CODE = "MGEE4B"  # appears in the page HTML; used to confirm the right page loaded
URL = ("https://business.currys.co.uk/catalogue/computing/laptops/macbook/"
       "apple-macbook-pro-16-2026-m5-max-2-tb-ssd-ram-48-gb-space-black/N428505W")

# A realistic browser User-Agent so Currys serves the normal page.
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"),
    "Accept-Language": "en-GB,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def fetch_page() -> str:
    resp = requests.get(URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text


def send_email_alert(detail: str, is_test: bool = False) -> None:
    key = os.environ.get("WEB3FORMS_KEY")
    if not key:
        print("ERROR: WEB3FORMS_KEY is not set - cannot send the email alert.")
        sys.exit(1)

    if is_test:
        subject = "TEST: Currys stock monitor is working"
        message = (
            "This is a one-time test of your Currys stock monitor. "
            "If you received this, in-stock alerts will arrive at this address.\n\n"
            f"{detail}\n\n"
            "You can ignore this message."
        )
    else:
        subject = "IN STOCK: MacBook Pro 16 M5 Max 48GB (MGEE4B/A) at Currys"
        message = (
            f"{PRODUCT_NAME}\n"
            f"(product code {PRODUCT_CODE}/A) appears to be BACK IN STOCK at Currys Business.\n\n"
            f"{detail}\n\n"
            f"Order here: {URL}\n\n"
            "-- Sent automatically by your GitHub Actions stock monitor."
        )

    resp = requests.post(
        "https://api.web3forms.com/submit",
        json={
            "access_key": key,
            "subject": subject,
            "from_name": "Currys Stock Monitor",
            "message": message,
        },
        timeout=30,
    )
    print(f"Email send status: {resp.status_code} {resp.text[:200]}")
    resp.raise_for_status()


def main() -> None:
    # Manual test mode: set TEST_EMAIL=1 to send a test email and exit, so you can
    # confirm delivery works without waiting for the item to restock.
    if os.environ.get("TEST_EMAIL") == "1":
        print("TEST_EMAIL mode - sending a test email.")
        send_email_alert("This is a TEST run - stock was not actually checked.", is_test=True)
        return

    try:
        html = fetch_page()
    except Exception as exc:  # network error, blocked, timeout, etc.
        # Do NOT email on errors - just log and exit cleanly so the job is green.
        print(f"Could not fetch the page ({exc}). Will try again next run.")
        return

    low = html.lower()

    # Sanity check: make sure we actually loaded the right product page.
    if PRODUCT_CODE.lower() not in low:
        print("Product code not found in page - the page may have changed or been "
              "blocked. Not alerting to avoid a false positive.")
        return

    still_out = "out of stock" in low
    can_buy = "add to basket" in low  # only present when purchasable

    if still_out and not can_buy:
        print("Still OUT OF STOCK. No action.")
        return

    # In stock (or at least no longer showing out-of-stock and shows a buy button).
    detail = "Detected: 'out of stock' message gone" + (
        " and an 'Add to basket' button is present." if can_buy else "."
    )
    print("IN STOCK detected! " + detail)
    send_email_alert(detail)


if __name__ == "__main__":
    main()
