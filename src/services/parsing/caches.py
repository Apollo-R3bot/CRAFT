import os
from datetime import datetime

from services.utils.utils import format_size, convert_webkit_time

def extract_caches(browser, cache_path, user_profile):
    cache_data = []

    for cache_dir in cache_path: 
        if not cache_dir or not os.path.exists(cache_dir):
            continue

        try:
            for root, _, files in os.walk(cache_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    size_bytes = os.path.getsize(file_path)
                    size = format_size(size_bytes)
                    created_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
                    last_used_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")

                    cache_data.append([
                        file,
                        size,
                        created_time,
                        last_used_time
                    ])

        except Exception as e:
                print(f"Error extracting cache from {cache_dir}: {e}")
    return cache_data