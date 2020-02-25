def handler(event, context):
    print("hello", event, context)
    return {"hello": "world"}
