import ast


def get_functions_from_file(filename):
    print(filename)
    with open(filename, "r", encoding="utf-8") as file:
        tree = ast.parse(file.read())

    # Filter the syntax tree nodes for Function Definitions
    functions = [
        node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    ]
    return functions


if __name__ == "__main__":
    print(get_functions_from_file("db/ReadCommands/superior_read_commands.py"))
