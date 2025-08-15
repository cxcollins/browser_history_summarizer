#!/usr/bin/env python3
import sqlite3
import argparse
from datetime import datetime
import requests
from typing import List, Tuple

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "granite3.2:2b"


def get_all_summaries(cursor) -> List[Tuple]:
    """Retrieve all summaries from database"""
    cursor.execute('''
        SELECT url, title, summary, visit_time
        FROM summaries
        ORDER BY visit_time DESC
    ''')
    return cursor.fetchall()


def format_summaries_for_llm(summaries: List[Tuple]) -> str:
    """Format summaries for LLM context"""
    formatted = []
    for i, (url, title, summary, visit_time) in enumerate(summaries):
        # Convert timestamp to readable date
        date_str = datetime.fromtimestamp(visit_time).strftime('%Y-%m-%d %H:%M')
        formatted.append(f"""
            Entry {i+1}:
            URL: {url}
            Title: {title}
            Date Visited: {date_str}
            Summary: {summary}
            """)
    return "\n".join(formatted)


def search_summaries_with_llm(query: str, summaries: List[Tuple], top_k: int = 3) -> List[int]:
    formatted_summaries = format_summaries_for_llm(summaries)

    prompt = f"""You are helping a user search through their browser history summaries.
        Given the user's query and a list of website summaries, identify the {top_k} most relevant entries.

        User Query: "{query}"

        Website Summaries:
        {formatted_summaries}

        Please respond with ONLY the entry numbers (e.g., "1, 5, 12") of the {top_k} most relevant summaries, separated by commas. 
        Consider relevance based on content similarity, topic matching, and potential usefulness to the query.
        Do not include any explanation, just the numbers."""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()

        # Parse the response to get entry numbers
        result = response.json()['response'].strip()
        entry_numbers = [int(x.strip()) - 1 for x in result.split(',')]  # Convert to 0-based indexing
        return entry_numbers[:top_k]

    except Exception as e:
        print(f"Error with LLM search: {e}")
        print("Make sure Ollama is running: ollama serve")
        return list(range(min(top_k, len(summaries))))  # Fallback to first N entries


def display_results(summaries: List[Tuple], selected_indices: List[int]):
    print("SEARCH RESULTS:" + "\n")

    for i, idx in enumerate(selected_indices, 1):
        if idx < len(summaries):
            url, title, summary, visit_time = summaries[idx]
            date_str = datetime.fromtimestamp(visit_time).strftime('%Y-%m-%d at %H:%M')

            print(f"\n Result {i}:")
            print(f"\n Title: {title}")
            print(f"\n URL: {url}")
            print(f"\n Visited: {date_str}")
            print(f"\n Summary: {summary}")
            print("\n" + "-" * 80)


def main():
    parser = argparse.ArgumentParser(description='Search browser history summaries using Granite3.2')
    parser.add_argument('query', help='Search query')
    parser.add_argument('-n', '--num-results', type=int, default=3,
                        help='Number of results to return (default: 3)')
    parser.add_argument('--db-path', default='summaries.db',
                        help='Path to SQLite database (default: summaries.db)')

    args = parser.parse_args()

    try:
        conn = sqlite3.connect(args.db_path)
        cursor = conn.cursor()

        # Get all summaries
        summaries = get_all_summaries(cursor)

        if not summaries:
            print("No summaries found in database. Run the main script first to populate it.")
            return

        print(f"\nSearching through {len(summaries)} summaries using Granite3.2")

        # Find and display relevant summaries
        selected_indices = search_summaries_with_llm(args.query, summaries, args.num_results)
        display_results(summaries, selected_indices)

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == '__main__':
    main()
