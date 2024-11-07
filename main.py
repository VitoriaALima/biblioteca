from flask import Flask, render_template, request, flash, url_for, redirect
import fdb

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vitoria bobona'

host = 'localhost'
database = r'C:\Users\Aluno\Downloads\BANCO\BANCO.FDB'
user = 'sysdba'
password = 'sysdba'

con = fdb.connect(host=host, database=database, user=user, password=password)


class Livros:
    def __init__(self, id_livros, titulo, autor, ano_publicacao):
        self.id_livro = id_livros
        self.titulo = titulo
        self.autor = autor
        self.ano_publicacao = ano_publicacao


@app.route('/')
def index():
    cursor = con.cursor()
    cursor.execute('SELECT id_livros, titulo, autor, ano_publicacao FROM livros')
    livros = cursor.fetchall()
    cursor.close()
    return render_template('livros.html', livros=livros)

@app.route('/novo')
def novo():
    return render_template('novo.html', titulo='Novo livro')

@app.route('/criar', methods=['POST'])
def criar():
    titulo = request.form['titulo']
    autor = request.form['autor']
    ano_publicacao = request.form['ano_publicacao']

    cursor = con.cursor()

    try:
        cursor.execute("select 1 from livros where titulo = ?", (titulo,))
        if cursor.fetchone():
            flash('Erro: Livro ja cadastrado')
            return redirect(url_for('novo'))
        cursor.execute("INSERT INTO livros (titulo, autor, ano_publicacao) VALUES (?, ?, ?)",
                       (titulo, autor, ano_publicacao))

        con.commit()

    finally:
        cursor.close()
    flash('Livro cadastrado com sucesso!')
    return redirect(url_for('index'))


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    cursor = con.cursor()  # Abre o cursor

    # Buscar o livro específico para edição
    cursor.execute("SELECT ID_LIVROS, TITULO, AUTOR, ANO_PUBLICACAO FROM livros WHERE ID_LIVROS = ?", (id,))
    livro = cursor.fetchone()

    if not livro:
        cursor.close()  # Fecha o cursor se o livro não for encontrado
        flash("Livro não encontrado!", "error")
        return redirect(url_for('index'))  # Redireciona para a página principal se o livro não for encontrado


    if request.method == 'POST':
        # Coleta os dados do formulário
        titulo = request.form['titulo']
        autor = request.form['autor']
        ano_publicacao = request.form['ano_publicacao']

        # Atualiza o livro no banco de dados
        cursor.execute("UPDATE livros SET TITULO = ?, AUTOR = ?, ANO_PUBLICACAO = ? WHERE ID_LIVROS = ?",
                       (titulo, autor, ano_publicacao, id))
        con.commit()  # Salva as mudanças no banco de dados
        cursor.close()  # Fecha o cursor
        flash("Livro atualizado com sucesso!", "success")
        return redirect(url_for('index'))  # Redireciona para a página principal após a atualização

    cursor.close()  # Fecha o cursor ao final da função, se não for uma requisição POST
    return render_template('editar.html', livro=livro, titulo='Editar Livro')  # Renderiza a página de edição

@app.route('/deletar/<int:id>', methods=['POST'])
def deletar(id):
    cursor = con.cursor()
    try:
        cursor.execute("DELETE FROM livros WHERE id_livros = ?", (id,))
        con.commit()
        flash("Livro excluido com sucesso!", "success")
    except Exception as e:
        con.rollback()
        flash("Erro ao escolher livro.", "error")
    finally:
        cursor.close()
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)