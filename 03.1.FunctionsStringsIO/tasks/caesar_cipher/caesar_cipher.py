def caesar_encrypt(message: str, n: int) -> str:
    """Encrypt message using caesar cipher

    :param message: message to encrypt
    :param n: shift
    :return: encrypted message
    """
    ans = []
    for i in message:
        if i.isalpha():
            offset = ord('A') if i.isupper() else ord('a')
            encrypted = chr((ord(i) - offset + n) % 26 + offset)
            ans.append(encrypted)
        else:
            ans.append(i)

    return ''.join(ans)
