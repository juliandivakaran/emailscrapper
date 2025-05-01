from datetime import time

from boto3 import resource
from boto3.dynamodb.conditions import Attr
from concurrent.futures import ThreadPoolExecutor
import uuid
import time


def chunk_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

table = resource('dynamodb').Table('keyword-generator')
index_record = resource('dynamodb').Table('temp-keyword-key-log')

def fetc_last_record():
    try:

        response = index_record.scan()
        items = response.get('Items', [])

        if items:
            stored_items = sorted(items, key=lambda x: int(x['last_index']), reverse=True)
            highest_item = stored_items[0]

            print("Retrieved highest item:", highest_item)
            print("Last index value:", highest_item.get('last_index'))
            print("Associated value:", highest_item.get('value'))
        else:
            print("No items found in the table.")

    except Exception as e:
        print("Exception in fetching last record:", e)

def batch_process_word(start_id, batch):
    try:

        with table.batch_writer() as batch_writer:
            for i, word in enumerate(batch):
                word_id = start_id + i
                batch_writer.put_item(Item={
                    'word_id': word_id,
                    'word': word
                })
        print(f"[Batch] Inserted batch of {len(batch)} words")
    except Exception as e:
        print(f"[Scrapper] Exception: fail to inser data {e}")


def print_scraped_words(words, max_workers=10):
    start_time = time.time()

    batch_size = 1000
    batches = list(chunk_list(words, batch_size))
    print(f"[Info] Total batches to insert: {len(batches)}")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for batch_index, batch in enumerate(batches):
            start_id = batch_index * batch_size
            futures.append(executor.submit(batch_process_word, start_id, batch))

        for future in futures:
            future.result()

    duration = time.time() - start_time

    index_record.put_item(Item={
        'last_index':str(len(words)),
    })
    print(f"[Done] Inserted {len(words)} words in {duration:.2f} seconds.")

if __name__ == "__main__":
    # Example: generate dummy data
    dummy_words = [f"keyword_{i}" for i in range(100000)]  # Change to 10_000_000 as needed
    print_scraped_words(dummy_words)
    fetc_last_record()




