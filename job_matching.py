import mysql.connector
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import pdfplumber


def extract_text_from_pdf(pdf_path):
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            full_text += page.extract_text()
    return full_text



def extract_skills_from_cv(cv_text):
    # List of predefined skills to look for (add more as needed)
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

    # Extract the skills by checking if keywords are in the CV text
    skills = [skill for skill in skill_keywords if skill.lower() in cv_text.lower()]

    return ', '.join(skills)


def fetch_jobs_from_db():
    try:
        # Establish a MySQL connection
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='karriere'
        )

        cursor = connection.cursor()

        # Fetch job listings from the database
        cursor.execute("SELECT title, company, description, skills, url FROM job_listings")
        jobs = cursor.fetchall()

        # Convert job listings into a DataFrame
        job_df = pd.DataFrame(jobs, columns=['title', 'company', 'description', 'skills', 'url'])

        return job_df

    except mysql.connector.Error as error:
        print(f"Error fetching jobs: {error}")
        return None

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def preprocess_text(text):
    # Remove non-alphanumeric characters, URLs, and extra spaces
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^A-Za-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text.lower()


def find_best_matching_job(cv_text, cv_skills, job_df):
    # Preprocess CV text and combine it with extracted skills
    cv_text_combined = preprocess_text(cv_text + ' ' + cv_skills)

    # Preprocess and vectorize job descriptions
    documents = job_df['description'].apply(preprocess_text).tolist()
    documents.append(cv_text_combined)  # Add CV text

    # Use TF-IDF for vectorization
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    # Compute cosine similarity between CV (last row) and all jobs
    cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])

    # Find the job with the highest similarity
    best_match_index = cosine_sim.argsort()[0][-1]
    best_match = job_df.iloc[best_match_index]

    return best_match


def main():
    # Path to the CV PDF file
    cv_pdf_path = 'cv.pdf'

    # Extract text from the PDF CV
    cv_text = extract_text_from_pdf(cv_pdf_path)

    # Extract skills from the CV
    cv_skills = extract_skills_from_cv(cv_text)

    # Fetch job listings from the database
    job_df = fetch_jobs_from_db()

    if job_df is not None and not job_df.empty:
        # Find the best matching job using cosine similarity
        best_job = find_best_matching_job(cv_text, cv_skills, job_df)

        # Display the best matching job
        print(f"Best matching job:\nTitle: {best_job['title']}\nCompany: {best_job['company']}")
        print(f"Link to the job: {best_job['url']}")
        print(f"Skills required for the job: {best_job['skills']}")
        print(f"Skills from CV: {cv_skills}")
    else:
        print("No jobs found in the database.")

if __name__ == "__main__":
    main()
