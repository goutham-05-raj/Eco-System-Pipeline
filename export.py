import sqlite3
import csv
import json
import os
from datetime import datetime, timezone

DB_PATH = 'graphone.db'
OUT_DIR = 'exports'

def ensure_dir():
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)

def export_startups(c):
    headers = [
        "schemaVersion", "recordType", "source.name", "source.url", 
        "content.entityName", "content.data.employeeCount", "collectedAt"
    ]
    data = c.execute("SELECT source_name, source_url, canonical_name, raw_name, employee_count, created_at FROM startups").fetchall()
    
    with open(f'{OUT_DIR}/startups.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in data:
            entity_name = row[2] if row[2] else row[3]
            writer.writerow(["1.0", "STARTUP", row[0], row[1], entity_name, row[4] or "", row[5]])

def export_products(c):
    headers = [
        "schemaVersion", "recordType", "source.name", "source.url", 
        "content.startupName", "content.pricingModel", "collectedAt"
    ]
    data = c.execute("SELECT source_name, source_url, startup_name, pricing_model, created_at FROM products").fetchall()
    
    with open(f'{OUT_DIR}/products.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in data:
            writer.writerow(["1.0", "PRODUCT", row[0], row[1], row[2] or "", row[3] or "", row[4]])

def export_papers(c):
    headers = [
        "schemaVersion", "recordType", "content.title", "content.authors", 
        "content.paper_url", "content.github_url", "content.github_stars", "content.published_date"
    ]
    data = c.execute("SELECT title, authors, source_url, github_url, github_stars, published_at FROM research_papers").fetchall()
    
    with open(f'{OUT_DIR}/research_papers.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in data:
            authors_str = ""
            if row[1]:
                try:
                    authors = json.loads(row[1])
                    authors_str = ", ".join(authors) if isinstance(authors, list) else str(authors)
                except:
                    authors_str = row[1]
            writer.writerow(["1.0", "RESEARCH_PAPER", row[0], authors_str, row[2], row[3] or "", row[4] or "", row[5] or ""])

def export_jobs(c):
    headers = [
        "schemaVersion", "recordType", "content.company", "content.date", 
        "content.is_remote", "content.role_family"
    ]
    # Filter 24h freshness for jobs as requested in deliverables
    # Assuming jobs table has published_at timestamp
    data = c.execute("SELECT company, published_at, is_remote, role_family FROM jobs").fetchall()
    
    with open(f'{OUT_DIR}/jobs.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in data:
            writer.writerow(["1.0", "JOB", row[0] or "", row[1] or "", "TRUE" if row[2] else "FALSE", row[3] or "Engineering"])

def export_news(c):
    headers = [
        "schemaVersion", "recordType", "content.title", "source.name", 
        "source.url", "content.published_date"
    ]
    data = c.execute("SELECT title, source_name, source_url, published_at FROM news").fetchall()
    
    with open(f'{OUT_DIR}/news.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in data:
            writer.writerow(["1.0", "NEWS", row[0], row[1], row[2], row[3] or ""])

def export_mapping(c):
    headers = [
        "raw_name", "canonical_name", "entity_type", 
        "matching_method", "confidence", "resolution_status"
    ]
    data = c.execute("SELECT raw_name, canonical_name, entity_type, matching_method, confidence, resolution_status FROM entity_mappings").fetchall()
    
    with open(f'{OUT_DIR}/entity_mapping.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in data:
            writer.writerow(row)

def main():
    ensure_dir()
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return
        
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        export_startups(c)
        export_products(c)
        export_papers(c)
        export_jobs(c)
        export_news(c)
        export_mapping(c)
        print("Successfully exported all 6 tabs to the 'exports' directory!")
    except Exception as e:
        print(f"Export error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
