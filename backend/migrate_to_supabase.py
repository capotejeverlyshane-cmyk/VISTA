import json
import os
from dotenv import load_dotenv
from supabase_client import supabase

def migrate_offices():
    try:
        with open("data/offices.json", "r", encoding="utf-8") as f:
            offices = json.load(f)
        for office in offices:
            data = {
                "office_id": office.get("office_id"),
                "name": office.get("name"),
                "head_of_office": office.get("head_of_office"),
                "contact": office.get("contact"),
                "location": office.get("location"),
                "operating_hours": office.get("operating_hours")
            }
            supabase.table("office_directory").insert(data).execute()
            print(f"Inserted office: {office.get('office_id')}")
    except Exception as e:
        print(f"Error migrating offices: {e}")

def migrate_articles():
    try:
        with open("data/articles.json", "r", encoding="utf-8") as f:
            articles = json.load(f)
        for article in articles:
            data = {
                "title": article.get("title"),
                "department": article.get("department"),
                "content": article.get("content"),
                "url": article.get("url")
            }
            supabase.table("articles").insert(data).execute()
            print(f"Inserted article: {article.get('title')}")
    except Exception as e:
        print(f"Error migrating articles: {e}")

def migrate_metrics():
    try:
        if not os.path.exists("models/metrics.json"):
            print("No metrics.json found, skipping.")
            return
            
        with open("models/metrics.json", "r", encoding="utf-8") as f:
            metrics = json.load(f)
            
        all_results = metrics.get("all_results", {})
        metrics_batch = []
        
        for model_key, model_info in all_results.items():
            # Upsert the model into nlp_models to satisfy Foreign Key constraints
            try:
                supabase.table("nlp_models").upsert({
                    "model_name": model_key,
                    "model_file": f"{model_key}.pkl",
                    "accuracy": model_info.get("accuracy", 0.0)
                }).execute()
            except Exception as e:
                print(f"Error upserting model {model_key}: {e}")
                continue
                
            report = model_info.get("report", {})
            for intent_name, scores in report.items():
                if isinstance(scores, dict) and "precision" in scores:
                    metrics_batch.append({
                        "model_name": model_key,
                        "intent_name": intent_name,
                        "precision": scores.get("precision", 0.0),
                        "recall": scores.get("recall", 0.0),
                        "f1_score": scores.get("f1-score", 0.0),
                        "support": int(scores.get("support", 0.0))
                    })
        
        # Batch insert the metrics
        chunk_size = 100
        for i in range(0, len(metrics_batch), chunk_size):
            chunk = metrics_batch[i:i+chunk_size]
            supabase.table("training_metrics").insert(chunk).execute()
            
        print(f"Inserted {len(metrics_batch)} training metrics.")
    except Exception as e:
        print(f"Error migrating metrics: {e}")

if __name__ == "__main__":
    print("Starting migration...")
    migrate_metrics()
    print("Migration complete!")
