import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re


# Function to get the HTML content of a page
def get_page_content(url):
    headers = {
        'User-Agent': '',
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


# Function to extract skills from a job description
def extract_skills(description):
    # Define a list of skills to look for (add more as needed)
    skill_keywords = [
        'JavaScript', 'C++', 'Data Modeling', 'AWS', 'DevOps', 'Data Science', 'Big Data', 'Databricks', 'Machine Learning',
        'APIs', 'Spark', 'Hadoop', 'CI/CD', 'Power BI', 'Data Engineering', 'ETL', 'Data Pipelines', 'Datenmodellierung',
        'Datenmanagement', 'Data Warehouse', 'Data Lakehouse', 'Data Lakes', 'Datenqualitätsanalyse', 'Datenentdeckung',
        'OLAP-Würfel', 'Datenvorbereitung', 'Datenintegration', 'Datenanalyse', 'SQL', 'T-SQL',
        'SSIS', 'Apache Hadoop', 'Apache Kafka', 'Apache NiFi', 'Apache Flink', 'Python',
        'C#', 'PowerShell', 'Microsoft SQL Server', 'Microsoft Azure', 'Microsoft Power Platform',
        'Microsoft Fabric', 'Java', 'Linux', 'Virtualisierung', 'Backup-Lösungen', 'Speicherlösungen',
        'Kommunikationsfähigkeit', 'Teamarbeit', 'Problemlösungsfähigkeiten', 'Kundenorientierung',
        'Strukturierte Arbeitsweise', 'Kreativität', 'Flexibilität', 'Selbstständigkeit',
        'Respekt und Empathie', 'Deutsch', 'Englisch', 'German', 'English', 'Technische Ausbildung', 'Berufserfahrung im Data Engineering',
        'Projekterfahrung', 'Verständnis von Bankgeschäftsmodellen', 'projektmanagement', 'erp', 'datenmodellen', 'computer science',
        'data processing'
    ]

    # Extract the skills by checking if keywords are in the description
    skills = [skill for skill in skill_keywords if skill.lower() in description.lower()]

    # Return the list of skills as a comma-separated string
    return ', '.join(skills)


def preprocess_text(text):
    # 1. Remove URLs
    text = re.sub(r'http\S+', '', text)  # Remove URLs

    # 2. Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)  # Remove emails

    # 3. Remove unwanted characters and extra spaces
    text = re.sub(r'[^A-Za-zÄäÖöÜüß\s/€.,-]', ' ', text)  # Remove non-German letters except some punctuation
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces and line breaks

    # 4. Convert to lowercase (optional, depending on the use case)
    text = text.lower()

    # 5. Remove duplicated lines or phrases (optional)
    seen_lines = set()
    lines = text.splitlines()
    unique_lines = []
    for line in lines:
        if line.strip() not in seen_lines:
            unique_lines.append(line)
            seen_lines.add(line.strip())

    return " ".join(unique_lines).strip()


# Function to parse detailed job descriptions from the individual job page
def parse_job_description(job_url):
    description = ''
    if job_url:
        job_content = get_page_content(job_url)
        if job_content:
            soup = BeautifulSoup(job_content, 'html.parser')
            description_tag = soup.find('div', class_='m-jobContent__jobText m-jobContent__jobText--standalone')

            # Extract text from all child tags inside the specified div
            if description_tag:
                # Loop through all elements (p, h1, h2, ul, li, etc.)
                for element in description_tag.find_all(True):
                    description += element.text.strip() + '\n'

    return preprocess_text(description.strip())


# Function to scrape job listings from a given URL
def scrape_karriere_jobs(query, location, num_pages=1):
    all_jobs = []
    base_url = f'https://www.karriere.at/jobs/{query}/{location}'

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
    num_pages = 1  # Number of pages to scrape
    location = 'wien'

    job_data = scrape_karriere_jobs(query, location, num_pages)

    if job_data:
        # Iterate through each job and fetch its detailed description
        for job in job_data:
            if job['url']:
                print(f"Scraping job details for: {job['title']} - {job['company']}")
                job_description = parse_job_description(job['url'])
                job['description'] = job_description

                # Extract skills from the job description
                job['skills'] = extract_skills(job_description)

                # Add random delay to avoid being blocked
                time.sleep(random.randint(3, 7))

        # Save to CSV
        df = pd.DataFrame(job_data)
        df.to_csv('karriere_at_data_engineer_listings.csv', index=False)
        print("Data saved to karriere_at_data_engineer_listings.csv")
    else:
        print("No job data found")


if __name__ == "__main__":
    main()