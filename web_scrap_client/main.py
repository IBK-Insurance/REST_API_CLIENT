import argparse
import sys
from datetime import datetime, date
from config import Config
from scraper import fetch_reviews
from emailer import send_email, format_reviews_html

def parse_args():
    parser = argparse.ArgumentParser(description='Scrape Google Play reviews and send email.')
    parser.add_argument(
        '--date', 
        type=str, 
        help='Target date in YYYY-MM-DD format. Defaults to today.',
        default=None
    )
    return parser.parse_args()

def main():
    # 1. Load and Validate Config
    try:
        Config.validate()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        sys.exit(1)

    # 2. Parse Arguments
    args = parse_args()
    if args.date:
        try:
            target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            sys.exit(1)
    else:
        target_date = date.today()

    print(f"Target execution date: {target_date}")

    # 3. Scrape Reviews
    try:
        reviews = fetch_reviews(Config.TARGET_APP_ID, target_date)
        print(f"Found {len(reviews)} reviews.")
    except Exception as e:
        print(f"Error scraping reviews: {e}")
        sys.exit(1)

    # 4. Filter & Send Email
    # Only send email if reviews found (or maybe send 'no reviews' email? Requester implies 'scraping content... then send', likely wants report regardless or only if content exists. I'll send regardless to confirm running, but note usually 'no content' is skipped. Let's send a summary.)
    
    # Requirement: "reviews content scraping... related content email send". 
    # If 0 reviews, sending a "0 reviews found" email is helpful for confirmation.
    
    subject = f"[Report] Google Play Reviews for {Config.TARGET_APP_ID} since {target_date}"
    body = format_reviews_html(reviews, target_date)
    
    print("----- Email Body Content -----")
    print(body)
    print("------------------------------")
    
    try:
        send_email(subject, body, Config.RECIPIENT_EMAILS)
    except Exception as e:
        print(f"Critical error sending email: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
