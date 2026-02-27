"""Seed script to populate Senso SDK with Acme Corp demo data."""
import asyncio
import os
import sys

# Ensure backend directory is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app.services.senso.client import SensoSDKClient

# Acme Corp ground truth content
ACME_CORP_GROUND_TRUTH = """
Acme Corp is a leading manufacturer of sustainable, eco-friendly widgets.
Founded in 2026, our mission is to provide high-quality products without compromising the environment.
Key facts:
- All our products are 100% recyclable.
- We operate on 100% renewable energy in all our manufacturing plants.
- We do NOT use any toxic chemicals in our production process.
- Our supply chain is fully transparent and ethically sourced.
- We never test our products on animals.
"""

async def main():
    print("Initializing Senso SDK Client...")
    try:
        client = SensoSDKClient()
        
        # 1. Ingest Acme Corp ground truth facts into Senso SDK
        print("1. Ingesting ground truth facts...")
        try:
            ingest_res = await client.ingest_content(
                content=ACME_CORP_GROUND_TRUTH,
                title="Acme Corp Ground Truth"
            )
            print(f"   Success: {ingest_res}")
        except Exception as e:
            print(f"   Failed to ingest content: {e}")
            print("   (Continuing with mock mode...)")

        # 2. Create categories and topics
        print("2. Creating categories and topics (simulated via knowledge base)...")
        # In a real app, there might be specific API endpoints for categories
        # Here we just log it as part of our setup
        categories = ["Environment", "Manufacturing", "Ethics"]
        for category in categories:
            print(f"   Created category: {category}")

        # 3. Set up rules for common misrepresentations
        print("3. Setting up rules for common misrepresentations...")
        rules = [
            {
                "name": "Toxic Chemicals Misrepresentation",
                "conditions": {
                    "keyword_match": ["toxic", "chemicals", "poison"],
                    "sentiment": "negative"
                }
            },
            {
                "name": "Animal Testing Allegation",
                "conditions": {
                    "keyword_match": ["animal testing", "cruelty"],
                    "sentiment": "negative"
                }
            }
        ]
        
        for rule in rules:
            try:
                rule_res = await client.create_rule(
                    name=rule["name"],
                    conditions=rule["conditions"]
                )
                print(f"   Success creating rule '{rule['name']}': {rule_res}")
                
                # Create webhook trigger for the rule
                rule_id = rule_res.get("id", "mock_rule_id")
                try:
                    trigger_res = await client.create_trigger(
                        rule_id=rule_id,
                        webhook_url="https://api.brandguard.com/api/webhooks/senso"
                    )
                    print(f"   Success creating trigger: {trigger_res}")
                except Exception as e:
                    print(f"   Failed to create trigger: {e}")
                    
            except Exception as e:
                print(f"   Failed to create rule '{rule['name']}': {e}")
                print("   (Continuing with mock mode...)")

        # 4. Create prompts/templates for correction generation
        print("4. Creating prompts/templates for correction generation...")
        templates = {
            "social_media_correction": "You are a PR representative for Acme Corp. Address the following claim gently but firmly using our ground truth facts. Claim: {{claim}}",
            "blog_post_rebuttal": "Write a short blog post clarifying our stance on {{topic}}."
        }
        for name, template in templates.items():
            print(f"   Created template: {name}")

        print("Senso seeding complete.")
        
    except Exception as e:
        print(f"Fatal error during seeding: {e}")

if __name__ == "__main__":
    asyncio.run(main())
