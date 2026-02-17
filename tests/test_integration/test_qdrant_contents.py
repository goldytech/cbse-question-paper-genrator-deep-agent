"""Diagnostic test to explore Qdrant database contents.

This test connects to Qdrant and displays:
1. All available collections
2. All chapters in the mathematics_10 collection
3. All topics within each chapter

Usage:
    uv run python tests/test_integration/test_qdrant_contents.py

Output:
    Prints a summary of available data in Qdrant for Class 10 Mathematics
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cbse_question_retriever.qdrant_client import qdrant_manager
from cbse_question_retriever.settings import settings


def get_all_chapters(collection_name: str) -> list:
    """Get all unique chapters from a collection.

    Args:
        collection_name: Name of the Qdrant collection

    Returns:
        List of unique chapter names
    """
    try:
        chapters = set()
        offset = None

        while True:
            results, offset = qdrant_manager.client.scroll(
                collection_name=collection_name,
                offset=offset,
                limit=100,
                with_payload=True,
            )

            for result in results:
                chapter = result.payload.get("chapter")
                if chapter:
                    chapters.add(chapter)

            if offset is None:
                break

        return sorted(list(chapters))
    except Exception as e:
        print(f"Error getting chapters: {e}")
        return []


def get_topics_for_chapter(collection_name: str, chapter: str) -> list:
    """Get all unique topics for a specific chapter.

    Args:
        collection_name: Name of the Qdrant collection
        chapter: Chapter name

    Returns:
        List of unique topic names
    """
    try:
        topics = set()
        offset = None

        while True:
            results, offset = qdrant_manager.client.scroll(
                collection_name=collection_name,
                offset=offset,
                limit=100,
                with_payload=True,
            )

            for result in results:
                if result.payload.get("chapter") == chapter:
                    topic = result.payload.get("topic")
                    if topic:
                        topics.add(topic)

            if offset is None:
                break

        return sorted(list(topics))
    except Exception as e:
        print(f"Error getting topics for {chapter}: {e}")
        return []


def main():
    """Main function to display Qdrant contents."""
    print("=" * 70)
    print("QDRANT DATABASE CONTENTS - DIAGNOSTIC TEST")
    print("=" * 70)
    print()

    # Show connection info
    print(f"Qdrant Host: {settings.qdrant.host}:{settings.qdrant.http_port}")
    print(f"API Key Set: {bool(settings.qdrant.api_key)}")
    print()

    # Get all collections
    try:
        collections = qdrant_manager.get_available_collections()
        print(f"Available Collections: {len(collections)}")
        for coll in collections:
            print(f"  - {coll}")
        print()
    except Exception as e:
        print(f"Error getting collections: {e}")
        return

    # Focus on mathematics_10 collection
    collection_name = "mathematics_10"

    if collection_name not in collections:
        print(f"ERROR: Collection '{collection_name}' not found!")
        print(f"Available collections: {collections}")
        return

    print(f"\nAnalyzing collection: {collection_name}")
    print("=" * 70)

    # Get all chapters
    chapters = get_all_chapters(collection_name)

    if not chapters:
        print("No chapters found in the collection.")
        return

    print(f"\nTotal Chapters: {len(chapters)}")
    print()

    # For each chapter, get topics
    total_topics = 0

    for i, chapter in enumerate(chapters, 1):
        topics = get_topics_for_chapter(collection_name, chapter)
        total_topics += len(topics)

        print(f"\nChapter {i}: {chapter}")
        print(f"  Topics ({len(topics)}):")

        if topics:
            for j, topic in enumerate(topics, 1):
                print(f"    {j}. {topic}")
        else:
            print("    (No topics found)")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total Chapters: {len(chapters)}")
    print(f"Total Topics: {total_topics}")
    print(f"Average Topics per Chapter: {total_topics / len(chapters):.1f}")
    print()

    # Show sample for blueprint matching
    print("\n" + "=" * 70)
    print("AVAILABLE TOPICS FOR BLUEPRINT MATCHING")
    print("=" * 70)
    print("\nWhen creating blueprints, use these exact topic names:")
    print()

    all_topics = []
    for chapter in chapters:
        topics = get_topics_for_chapter(collection_name, chapter)
        all_topics.extend(topics)

    for i, topic in enumerate(sorted(all_topics), 1):
        print(f"{i:2d}. {topic}")


if __name__ == "__main__":
    main()
