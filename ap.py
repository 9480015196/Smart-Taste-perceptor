from google.generativeai import Client

client = Client()
models = client.list_models()
print(models)