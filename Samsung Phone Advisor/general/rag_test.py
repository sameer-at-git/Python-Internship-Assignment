
#!/usr/bin/env python3
"""
Test script for the RAG module
"""

import logging
from rag_module import RAGModule

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    rag = RAGModule()
    
    print("Samsung Phone RAG Module Test")
    print("=" * 50)
    
    while True:
        user_query = input("\nEnter your query (or 'quit' to exit): ").strip()
        
        if user_query.lower() in ['quit', 'exit', 'q']:
            break
        
        if not user_query:
            continue
        
        try:
            result = rag.process_query(user_query)
            
            print(f"\n📊 Query Analysis:")
            print(f"   Intent: {result['intent']}")
            print(f"   Focus Area: {result['focus_area']}")
            print(f"   Confidence: {result['confidence']}")
            print(f"   Results Found: {result['total_results']}")
            print(f"   Query Time: {result['query_time_ms']}ms")
            
            if result['matched_phones']:
                print(f"\n📱 Matching Phones:")
                for i, phone in enumerate(result['matched_phones'][:5], 1):
                    print(f"\n   {i}. {phone['model_name']}")
                    if phone.get('release_date'):
                        print(f"      Released: {phone['release_date']}")
                    if phone.get('display_size_inches'):
                        print(f"      Display: {phone['display_size_inches']}'' {phone.get('display_type', '')}")
                    if phone.get('battery_mah'):
                        print(f"      Battery: {phone['battery_mah']} mAh")
                    if phone.get('main_camera_mp'):
                        print(f"      Main Camera: {phone['main_camera_mp']} MP")
                    if phone.get('price_usd'):
                        print(f"      Price: ${phone['price_usd']}")
            
            else:
                print("\n❌ No phones found matching your query.")
                
        except Exception as e:
            print(f"\n❌ Error processing query: {e}")

if __name__ == "__main__":
    main()