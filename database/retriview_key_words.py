from database.database import table
import time

def get_keyword_list():
    seen_ids =set()
    keywords = []
    last_evaluated_key =None

    while True:
        scan_args = {
            'ProjectionExpression':'word_id,word',
            'Limit':1000,
        }

        if last_evaluated_key:
            scan_args['ExclusiveStartKey'] = last_evaluated_key

        response = table.scan(**scan_args)
        last_evaluated_key = response.get('LastEvaluatedKey', None)

        for item in response['Items']:
            word_id = item['word_id']
            word = item['word']

            if word_id not in seen_ids:
                seen_ids.add(word_id)
                keywords.append(word)

        if not last_evaluated_key:
            break

    return keywords

    """
    start_time = time.time()
    duration = 360  # Run for 6 minutes
    seen_ids = set()
    last_evaluated_key = None

    while True:
        elapsed_time = time.time() - start_time

        if elapsed_time >= duration:
            print("Elapsed time:", round(elapsed_time, 1), "seconds. Stopping.")
            break

        print("Elapsed time:", round(elapsed_time, 1), "seconds")

        # Build scan arguments
        scan_args = {
            'ProjectionExpression': 'word_id, word',
            'Limit': 100  # Scan more items to increase chance of new IDs
        }

        if last_evaluated_key:
            scan_args['ExclusiveStartKey'] = last_evaluated_key

        response = table.scan(**scan_args)

        # Save the pagination key for next scan
        last_evaluated_key = response.get('LastEvaluatedKey', None)

        count = 0
        for item in response['Items']:
            word_id = item['word_id']

            if word_id not in seen_ids:
                seen_ids.add(word_id)
                print(f"word_id: {word_id}, word: {item['word']}")
                count += 1

            if count >= 100:
                break  # Limit to 10 new items per second

        # If we reached end of table, restart
        if not last_evaluated_key:
            last_evaluated_key = None

        time.sleep(1)

if __name__ == '__main__':
    fetc_keywords()
    """
