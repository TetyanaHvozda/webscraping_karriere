import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random


# Function to get the HTML content of a page
def get_page_content(url):
    headers = {
        'User-Agent': 'your_user_agent',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/',
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to retrieve page: {response.status_code}")
        return None


# Function to parse job data from a page
def parse_job_data(soup):
    jobs = []

    # Find all job listing items
    job_items = soup.find_all('li', class_='m-jobsList__item')

    for item in job_items:
        # Extract job title
        title_tag = item.find('a', class_='m-jobsListItem__titleLink')
        job_title = title_tag.text.strip() if title_tag else None

        # Construct the job URL
        job_url = title_tag['href'] if title_tag and 'href' in title_tag.attrs else None

        # Extract company name
        company_tag = item.find('a', class_='m-jobsListItem__companyName')
        company_name = company_tag.text.strip() if company_tag else None

        # Extract location(s), job type, home office, and salary
        pill_tags = item.find_all('span', class_='m-jobsListItem__pill')

        # Extract job location(s)
        location_tag = item.find('span', class_='m-jobsListItem__locations')
        job_locations = [loc.text.strip() for loc in
                         location_tag.find_all('a', class_='m-jobsListItem__location')] if location_tag else None

        # Extract job type, home office, and salary (from pill tags)
        job_type = None
        home_office = None
        salary = None

        for pill in pill_tags:
            text = pill.text.strip()
            if 'Vollzeit' in text or 'Teilzeit' in text:
                job_type = text
            elif 'Homeoffice' in text:
                home_office = text
            elif '€' in text:
                salary = text


        # Add parsed job data to the list
        jobs.append({
            'title': job_title,
            'company': company_name,
            'locations': job_locations,
            'type': job_type,
            'home_office': home_office,
            'salary': salary,
            'url': job_url
        })

    return jobs


# Function to scrape job listings from a given URL
def scrape_karriere_jobs(query, location, num_pages=1):
    all_jobs = []
    base_url = f'https://www.karriere.at/jobs/{query}/wien'

    for page in range(1, num_pages + 1):
        url = f"{base_url}?page={page}"
        print(f"Scraping page {page}: {url}")

        page_content = get_page_content(url)
        if page_content:
            soup = BeautifulSoup(page_content, 'html.parser')
            jobs = parse_job_data(soup)
            all_jobs.extend(jobs)

        # Add random delay to avoid being blocked
        time.sleep(random.randint(5, 10))

    return all_jobs


# Main function to run the scraper and save data to a CSV file
def main():
    query = 'data-engineer'  # Replace with your desired job title (URL-friendly)
    num_pages = 2  # Number of pages to scrape

    job_data = scrape_karriere_jobs(query, num_pages)

    if job_data:
        # Save to CSV
        df = pd.DataFrame(job_data)
        df.to_csv('karriere_at_data_engineer_listings.csv', index=False)
        print("Data saved to karriere_at_data_engineer_listings.csv")
    else:
        print("No job data found")


if __name__ == "__main__":
    main()
