from flask import Flask, request, render_template_string
import re
import ply.lex as lex

app = Flask(__name__)

# Definición de tokens para el analizador léxico
tokens = [
    'PHP_OPEN', 'PHP_CLOSE', 'PR', 'ID', 'NUM', 'SYM', 'ERR'
]

t_PHP_OPEN = r'<\?php'
t_PHP_CLOSE = r'\?>'
t_PR = r'\b(Inicio|cadena|proceso|si|ver|Fin)\b'
t_ID = r'\b[a-zA-Z_][a-zA-Z_0-9]*\b'
t_NUM = r'\b\d+\b'
t_SYM = r'[;{}()\[\]=<>!+-/*]'
t_ERR = r'.'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Carácter ilegal '{t.value[0]}'")
    t.lexer.skip(1)

# Plantilla HTML para mostrar resultados
html_template = '''
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <style>
    body {
      background-color: #2a3b4c;
      color: #ffffff;
      font-family: Arial, sans-serif;
    }
    .container {
      width: 80%;
      margin: 20px auto;
      padding: 20px;
      background-color: #3b4f63;
      border-radius: 8px;
    }
    h1 {
      text-align: center;
    }
    textarea {
      width: 100%;
      height: 200px;
      border: 1px solid #5a6b7d;
      border-radius: 8px;
      padding: 10px;
      margin-bottom: 10px;
      font-size: 16px;
      background-color: #4b5d70;
      color: #ffffff;
    }
    input[type="submit"] {
      background-color: #ff4b4b;
      color: white;
      padding: 10px 20px;
      border: none;
      border-radius: 5px;
      cursor: pointer;
      font-size: 18px;
      margin: 0 10px;
    }
    input[type="submit"]:hover {
      background-color: #e03d3d;
    }
    pre {
      white-space: pre-wrap;
      word-wrap: break-word;
      font-size: 16px;
    }
    .error {
      color: red;
      font-weight: bold;
    }
    .results {
      margin-top: 20px;
      padding: 20px;
      background-color: #4b5d70;
      border-radius: 8px;
    }
    h2 {
      text-align: center;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 20px;
    }
    th, td {
      border: 1px solid #5a6b7d;
      padding: 8px;
      text-align: center;
    }
    th {
      background-color: #3b4f63;
      color: #ffffff;
    }
    .buttons {
      text-align: center;
      margin-bottom: 20px;
    }
  </style>
  <title>Analizador Léxico, Sintáctico y Semántico</title>
</head>
<body>
  <div class="container">
    <h1>Analizador Léxico, Sintáctico y Semántico</h1>
    <form method="post">
      <textarea name="code" rows="10" cols="50">{{ code }}</textarea><br>
      <div class="buttons">
        <input type="submit" name="action" value="Analizar Léxico">
        <input type="submit" name="action" value="Analizar Sintáctico">
        <input type="submit" name="action" value="Analizar Semántico">
      </div>
    </form>
    <div class="results">
      <h2>Análisis Léxico</h2>
      <table>
        <tr>
          <th>Tokens</th><th>PHP_OPEN</th><th>PHP_CLOSE</th><th>PR</th><th>ID</th><th>Números</th><th>Símbolos</th><th>Error</th>
        </tr>
        {% for row in lexical %}
        <tr>
          <td>{{ row[0] }}</td><td>{{ row[1] }}</td><td>{{ row[2] }}</td><td>{{ row[3] }}</td><td>{{ row[4] }}</td><td>{{ row[5] }}</td><td>{{ row[6] }}</td><td>{{ row[7] }}</td>
        </tr>
        {% endfor %}
        <tr>
          <td>Total</td><td>{{ total['PHP_OPEN'] }}</td><td>{{ total['PHP_CLOSE'] }}</td><td>{{ total['PR'] }}</td><td>{{ total['ID'] }}</td><td>{{ total['NUM'] }}</td><td>{{ total['SYM'] }}</td><td>{{ total['ERR'] }}</td>
        </tr>
      </table>
    </div>
    <div class="results">
      <h2>Análisis Sintáctico</h2>
      <p>{{ syntactic }}</p>
    </div>
    <div class="results">
      <h2>Análisis Semántico</h2>
      <p>{{ semantic }}</p>
    </div>
  </div>
</body>
</html>
'''

def analyze_lexical(code):
    lexer = lex.lex()
    lexer.input(code)
    results = {'PHP_OPEN': 0, 'PHP_CLOSE': 0, 'PR': 0, 'ID': 0, 'NUM': 0, 'SYM': 0, 'ERR': 0}
    rows = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        row = [''] * 8
        if tok.type in results:
            results[tok.type] += 1
            row[list(results.keys()).index(tok.type)] = 'x'
        rows.append(row)
    return rows, results

def analyze_syntactic(code):
    errors = []

    # Verificar la estructura de apertura y cierre de PHP
    if not code.startswith("<?php"):
        errors.append("El código debe comenzar con '<?php'.")
    if not code.endswith("?>"):
        errors.append("El código debe terminar con '?>'.")

    # Verificar la estructura de "Inicio" y "Fin"
    if "Inicio;" not in code or "Fin;" not in code:
        errors.append("El código debe contener 'Inicio;' y 'Fin;'.")

    lines = code.split('\n')
    for i, line in enumerate(lines):
        # Ignorar líneas que no requieren punto y coma
        if line.strip() and not line.strip().endswith(';') and not line.strip().endswith('{') and not line.strip().endswith('}') and "si (" not in line and "{" not in line and "}" not in line and "Inicio;" not in line and "Fin;" not in line:
            errors.append(f"Falta punto y coma al final de la línea {i + 1}.")

    if not errors:
        return "Sintaxis correcta"
    else:
        return " ".join(errors)

def analyze_semantic(code):
    errors = []
    variable_types = {}

    # Identificar y almacenar los tipos de las variables
    for var_declaration in re.findall(r"\b(cadena|entero)\s+\$?(\w+)\s*=\s*(.*);", code):
        var_type, var_name, value = var_declaration
        variable_types[var_name] = var_type
        if var_type == "cadena" and not re.match(r'^".*"$', value):
            errors.append(f"Error semántico en la asignación de '{var_name}'. Debe ser una cadena entre comillas.")
        elif var_type == "entero" and not re.match(r'^\d+$', value):
            errors.append(f"Error semántico en la asignación de '{var_name}'. Debe ser un valor numérico.")

    # Verificar comparaciones lógicas
    logical_checks = re.findall(r"si\s*\((.+)\)", code)
    for check in logical_checks:
        match = re.search(r"(\$?\w+)\s*(==|!=)\s*(\$?\w+|\".*\"|\d+)", check)
        if match:
            left_var, _, right_var = match.groups()
            left_type = variable_types.get(left_var.strip('$'), None)
            right_type = 'cadena' if right_var.startswith('"') or not right_var.isdigit() else 'entero'
            if left_type and right_type and left_type != right_type:
                errors.append(f"Error semántico en la condición 'si ({check})'. No se puede comparar {left_type} con {right_type}.")

    if not errors:
        return "Uso correcto de las estructuras semánticas"
    else:
        return " ".join(errors)

@app.route('/', methods=['GET', 'POST'])
def index():
    code = ''
    lexical_results = []
    syntactic_results = ''
    semantic_results = ''
    total = {'PHP_OPEN': 0, 'PHP_CLOSE': 0, 'PR': 0, 'ID': 0, 'NUM': 0, 'SYM': 0, 'ERR': 0}
    if request.method == 'POST':
        code = request.form['code']
        if 'action' in request.form:
            action = request.form['action']
            if action == 'Analizar Léxico':
                lexical_results, total = analyze_lexical(code)
            elif action == 'Analizar Sintáctico':
                syntactic_results = analyze_syntactic(code)
            elif action == 'Analizar Semántico':
                semantic_results = analyze_semantic(code)
    return render_template_string(html_template, code=code, lexical=lexical_results, syntactic=syntactic_results, semantic=semantic_results, total=total)

if __name__ == '__main__':
    app.run(debug=True)
