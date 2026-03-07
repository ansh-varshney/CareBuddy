"""
Knowledge Base Ingestion Script

Run: python -m knowledge_base.ingest
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.knowledge_base import seed_knowledge_base


def main():
    print("=" * 50)
    print("  CareBuddy — Knowledge Base Ingestion")
    print("=" * 50)

    stats = seed_knowledge_base()
    print("\n✅ Knowledge base ready!")
    print(f"   Total documents: {stats['total_documents']}")
    print(f"   Collection: {stats['collection_name']}")


if __name__ == "__main__":
    main()
