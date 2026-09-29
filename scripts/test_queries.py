"""
CLI Diagnostic utility to execute polar queries and benchmark latency.
"""
import sys
from pathlib import Path

# Configure utf-8 console output for Windows cmd/powershell
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from agents.graph import execute_polar_query

TEST_QUERIES = [
    "Tell me about Maitri station.",
    "What datasets are available for Maitri?",
    "What was the average temperature at Maitri in 2012?",
    "Show me photographs of Bharati station.",
    "Explain India's Antarctic research to a school student.",
    "What research was conducted during the 15th Arctic Expedition?"
]

def main():
    print("=" * 70)
    print("NCPOR Polar Science AI Engine - Benchmark & Query Evaluation")
    print("=" * 70)
    for q in TEST_QUERIES:
        print(f"\n[QUERY]: {q}")
        res = execute_polar_query(q)
        print(f"  -> Route: {res.get('route')}")
        print(f"  -> Latency: {res.get('response_time_ms', 0.0):.2f} ms")
        preview = res.get('final_answer', '')[:120].replace('\n', ' ')
        print(f"  -> Final Answer Preview: {preview}...")
        print(f"  -> Groundedness Passed: {res.get('groundedness_passed')}")

if __name__ == "__main__":
    main()
