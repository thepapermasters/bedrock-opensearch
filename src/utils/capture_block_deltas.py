import json


def capture_content_block_deltas(streaming_response):
    # Initialize an empty list to capture text deltas
    deltas = []

    # Iterate over the streaming response
    for sr in streaming_response["body"]:
        # Load the chunk content as a dictionary
        chunk = json.loads(sr["chunk"]["bytes"])

        # Check if the chunk type is 'content_block_delta'
        if chunk["type"] == "content_block_delta":
            # Get the text from the delta and add to the list
            deltas.append(chunk["delta"].get("text", ""))
    print("deltas:::", deltas)
    if len(deltas) > 0:
        # Concatenate the text deltas and convert to a dictionary
        concatenate = ''.join(deltas)
        print("JSON LOADS::", concatenate)
        return json.loads(concatenate)
    else:
        return deltas[0]
