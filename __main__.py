from language import Language


def main():
    with open('syntax.txt', 'r', encoding='utf-8') as file:
        language = Language.create(file)

    result = language.syntaxes.get('문장').create(language)
    print(result.stringify())
    print(result.pformat())


if __name__ == '__main__':
    main()
