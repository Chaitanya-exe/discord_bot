def get_response(user_input: str) -> str:
    lowered: str = user_input.lower()

    if lowered == '': 
        return "Well you're awfully silent"
    elif "hello" in lowered:
        return "Hello world"
    else:
        return "I don't understand what you're sayin??"
    
def parser(argu: str) -> list[str]:
    chars = []
    for char in argu:
        chars.append(char)
    return chars