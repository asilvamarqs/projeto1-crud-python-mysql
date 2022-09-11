from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from CadAluno import Ui_CadAlunos
import pymysql.cursors


class Banco:
    def __init__(self):
        self.conexao = pymysql.connect(host='localhost',
                                       user='root',
                                       password='password',
                                       database='escola',
                                       cursorclass=pymysql.cursors.DictCursor)

    def listarTodos(self):
        with self.conexao.cursor() as cursor:
            try:
                sql = "SELECT * FROM aluno"
                cursor.execute(sql)
                resultado = cursor.fetchall()
                return resultado
            except Exception as erro:
                print(f'Erro ao listar os alunos. Erro: {erro}')

    def listarPorNome(self, nome):
        with self.conexao.cursor() as cursor:
            try:
                sql = "SELECT * FROM aluno WHERE nome LIKE %s"
                cursor.execute(sql, (f'%{nome}%',))
                resultado = cursor.fetchall()
                return resultado
            except Exception as erro:

                print(f'Erro ao listar por nome. Erro: {erro}')

    def inserir(self, nome, idade, curso):
        with self.conexao.cursor() as cursor:
            try:
                sql = "INSERT INTO aluno (nome, idade, curso) VALUES (%s, %s, %s)"
                cursor.execute(sql, (nome, idade, curso))
                self.conexao.commit()
            except Exception as erro:
                print(f'Erro ao inserir. Erro: {erro}')

    def excluir(self, matricula):
        with self.conexao.cursor() as cursor:
            try:
                sql = "DELETE FROM aluno WHERE matricula = %s"
                cursor.execute(sql, matricula)
                self.conexao.commit()

            except Exception as erro:
                print(f'Erro ao deletar. Erro: {erro}')

    def alterar(self, matricula, nome, idade, curso):
        with self.conexao.cursor() as cursor:
            try:
                sql = "UPDATE aluno SET nome = %s, idade = %s, curso = %s WHERE " \
                      "matricula = %s"
                cursor.execute(sql, (nome, idade, curso, matricula))
                self.conexao.commit()
            except Exception as erro:
                print(f'Erro ao editar. Erro: {erro}')


class Window(QMainWindow, Ui_CadAlunos):
    def __init__(self):
        super().__init__()

        self.setupUi(self)

        self.bd = Banco()
        self.carregarTabela()

        self.btn_editar.setEnabled(False)
        self.btn_excluir.setEnabled(False)

        # eventos
        self.tb_alunos.cellClicked.connect(self.tabelaClicou)
        self.btn_novo.clicked.connect(self.cadastrar)
        self.btn_excluir.clicked.connect(self.deletar)
        self.btn_editar.clicked.connect(self.atualizar)
        self.txt_buscar.textChanged.connect(self.carregarTabela)

    def carregarTabela(self):
        campo = self.txt_buscar.text()

        if campo == "":
            resultado = self.bd.listarTodos()
        else:
            resultado = self.bd.listarPorNome(campo)

        self.tb_alunos.setRowCount(len(resultado))
        linha = 0

        for aluno in resultado:
            self.tb_alunos.setItem(linha, 0, QtWidgets.QTableWidgetItem(str(aluno['matricula'])))
            self.tb_alunos.setItem(linha, 1, QtWidgets.QTableWidgetItem(aluno['nome']))
            self.tb_alunos.setItem(linha, 2, QtWidgets.QTableWidgetItem(str(aluno['idade'])))
            self.tb_alunos.setItem(linha, 3, QtWidgets.QTableWidgetItem(aluno['curso']))
            linha += 1

    def tabelaClicou(self, row):
        matricula = self.tb_alunos.item(row, 0).text()
        nome = self.tb_alunos.item(row, 1).text()
        idade = self.tb_alunos.item(row, 2).text()

        self.txt_matricula.setText(matricula)
        self.txt_nome.setText(nome)
        self.txt_idade.setText(idade)

        self.habilitarBotoes()

    def cadastrar(self):
        nome = self.txt_nome.text()
        idade = int(self.txt_idade.text())
        curso = self.cb_curso.currentText()

        self.bd.inserir(nome, idade, curso)
        QMessageBox.information(self, "Sucesso!", "Aluno cadastrado com sucesso!")
        self.limparCampos()
        self.carregarTabela()

    def atualizar(self):
        matricula = int(self.txt_matricula.text())
        nome = self.txt_nome.text()
        idade = int(self.txt_idade.text())
        curso = self.cb_curso.currentText()

        resultado = QMessageBox.question(self, "Tem certeza?", "Deseja atualizar os dados?",
                                         QMessageBox.Yes | QMessageBox.No)

        if resultado == QMessageBox.Yes:
            self.bd.alterar(matricula, nome, idade, curso)
            QMessageBox.information(self, "Sucesso!", "Dados atualizados com sucesso!")
            self.limparCampos()
            self.desabilitarBotoes()
            self.carregarTabela()

    def deletar(self):
        matricula = int(self.txt_matricula.text())

        resultado = QMessageBox.question(self, "Tem certeza?", "Deseja excluir o aluno?",
                                         QMessageBox.Yes | QMessageBox.No)

        if resultado == QMessageBox.Yes:
            self.bd.excluir(matricula)
            QMessageBox.information(self, "Sucesso!", "Aluno excluido com sucesso!")
            self.limparCampos()
            self.desabilitarBotoes()
            self.carregarTabela()

    def limparCampos(self):
        self.txt_matricula.setText("")
        self.txt_nome.setText("")
        self.txt_idade.setText("")

    def habilitarBotoes(self):
        self.btn_editar.setEnabled(True)
        self.btn_excluir.setEnabled(True)

    def desabilitarBotoes(self):
        self.btn_editar.setEnabled(False)
        self.btn_excluir.setEnabled(False)


app = QApplication([])
window = Window()
window.show()
app.exec()
