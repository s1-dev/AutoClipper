from typing import Callable, Optional

def getAndValidateUserInput(
    inputText: str,
    errorText: str,
    conditional: Callable[[str], bool]
) -> Optional[str]: 
    validInput = False
    while not validInput:
        userInput = input(inputText)
        if conditional(userInput):
            return userInput
        else:
            print(errorText)
    return None
