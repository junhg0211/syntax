from random import choice


VALUE_STRING = 1
VALUE_NAME = 2

class Rule(list):
    pass


class Result(list):
    def stringify(self) -> str:
        result = list()
        for syntax in self:
            result.append(syntax.stringify())
        return ' '.join(result)

    def pformat(self) -> str:
        result = list()
        for syntax in self:
            result.append(syntax.pformat())
        result = ' '.join(result)
        return f'{result}'


class ResultValue:
    def __init__(self, type_: int, value):
        self.type = type_
        self.value = value

    def stringify(self) -> str:
        if self.type == VALUE_STRING:
            return self.value

        if self.type == VALUE_NAME:
            return self.value[1].stringify()

    def pformat(self):
        if self.type == VALUE_STRING:
            return self.value

        if self.type == VALUE_NAME:
            return f'[{self.value[0]} {self.value[1].pformat()}]'


depth = 0

class Syntax:
    next_id = 0

    def __init__(self, name: str):
        self.name = name

        self.rules = list()
        self.id = Syntax.next_id
        Syntax.next_id += 1

    def __repr__(self) -> str:
        return f'<Syntax {self.name} #{self.id}>'

    def create(self, language: 'Language'):
        global depth
        # print(depth, self.name)
        depth += 1

        result = Result()
        rule = choice(self.rules)

        for syntax in rule:
            if syntax[0] == VALUE_STRING:
                result.append(ResultValue(VALUE_STRING, syntax[1]))
                continue

            if syntax[0] == VALUE_NAME:
                result.append(ResultValue(VALUE_NAME,
                    (syntax[1], language.syntaxes
                        .get(syntax[1])
                        .create(language))))

        depth -= 1
        return result


MODE_NONE = 0
MODE_DEFINE = 1

class Language:
    @staticmethod
    def create(fp):
        language = Language()
        while line := fp.readline():
            language.interpret_line(line)
        return language

    def __init__(self):
        self.syntaxes = dict()

    def interpret_line(self, line: str):
        tokens = line.strip().split(' ')
        stack = list()
        mode = MODE_NONE

        tokens.append('\n')

        # -- variables
        # define mode
        name = ''
        syntax = None
        rule = Rule()
        stringing = False
        string_content = ''

        # -- interpreter
        first = None
        while tokens:
            stack.append(first)
            first = tokens.pop(0)

            if first == '#':
                break

            if mode == MODE_NONE:
                if first == '::=':
                    if not stack:
                        raise SyntaxError('syntax name is not defined')

                    mode = MODE_DEFINE
                    name = stack[-1]
                    syntax = Syntax(name)

                continue

            if mode == MODE_DEFINE:
                if first == '\n':
                    syntax.rules.append(rule)
                    self.syntaxes[name] = syntax
                    break

                if first == '|':
                    syntax.rules.append(rule)
                    rule = Rule()
                    string_content = ''
                    continue

                if first.startswith('"'):
                    if first.endswith('"'):
                        content = first[1:-1]
                        string_content += content

                        rule.append((VALUE_STRING, string_content))
                        string_content = ''
                        continue

                    stringing = True
                    content = first[1:]
                    string_content += content
                    continue

                if first.endswith('"'):
                    if not stringing:
                        raise SyntaxError('string end found, yet not parsing string')

                    content = first[:-1]
                    string_content += content
                    stringing = False
                    continue

                rule.append((VALUE_NAME, first))
