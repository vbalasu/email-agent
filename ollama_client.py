def test_call_ollama():
    print(call_ollama())

def call_ollama(model='mistral', prompt='Tell me a joke'):
    from langchain.chat_models.ollama import ChatOllama

    # Get the configuration
    import configparser
    config = configparser.ConfigParser()
    config.read('settings.conf')
    base_url = config.get('DEFAULT', 'base_url')
    model = config.get('DEFAULT', 'model')
    print('base_url', base_url, 'model', model)

    ollama_client = ChatOllama(base_url=base_url, model=model)
    return ollama_client.invoke(prompt)