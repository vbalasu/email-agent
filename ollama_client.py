def test_call_ollama():
    print(call_ollama())

def call_ollama(prompt='Tell me a joke'):
    from langchain.chat_models.ollama import ChatOllama
    from langchain_core.output_parsers.string import StrOutputParser

    # Get the configuration
    import configparser
    config = configparser.ConfigParser()
    config.read('settings.conf')
    base_url = config.get('DEFAULT', 'base_url')
    model = config.get('DEFAULT', 'model')
    # print('base_url', base_url, 'model', model)

    ollama_client = ChatOllama(base_url=base_url, model=model)
    chain = ollama_client | StrOutputParser()
    return chain.invoke(prompt)