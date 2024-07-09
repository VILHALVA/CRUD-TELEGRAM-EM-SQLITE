import sqlite3
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

class GerenciadorUsuarios:
    def __init__(self):
        self.conexao = sqlite3.connect('cadastro.db')
        self.cursor = self.conexao.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios
                               (nome TEXT, idade INTEGER)''')
        self.conexao.commit()

    def adicionar_usuario(self, nome, idade):
        sql = "INSERT INTO usuarios (nome, idade) VALUES (?, ?)"
        val = (nome, idade)
        self.cursor.execute(sql, val)
        self.conexao.commit()

    def listar_usuarios(self):
        self.cursor.execute("SELECT nome, idade FROM usuarios")
        return self.cursor.fetchall()

    def atualizar_usuario(self, nome_antigo, novo_nome, nova_idade):
        sql = "UPDATE usuarios SET nome = ?, idade = ? WHERE nome = ?"
        val = (novo_nome, nova_idade, nome_antigo)
        self.cursor.execute(sql, val)
        self.conexao.commit()

    def excluir_usuario(self, nome):
        sql = "DELETE FROM usuarios WHERE nome = ?"
        val = (nome,)
        self.cursor.execute(sql, val)
        self.conexao.commit()

async def start(update, context):
    keyboard = [
        [InlineKeyboardButton("ADICIONAR", callback_data='add')],
        [InlineKeyboardButton("EXIBIR A LISTA", callback_data='list')],
        [InlineKeyboardButton("ATUALIZAR", callback_data='update')],
        [InlineKeyboardButton("EXCLUIR", callback_data='delete')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('👋OLÁ! EU SOU UM BOT BÁSICO DE CRUD. MINHA PRINCIPAL FUNCIONALIDADE É GERENCIAR USUÁRIOS COM DATABASE. \n🤖CLIQUE EM UMA OPÇÃO:', reply_markup=reply_markup)

    context.user_data['gerenciador'] = GerenciadorUsuarios()

async def button(update, context):
    query = update.callback_query
    data = query.data

    if data == 'add':
        await query.message.reply_text('Digite o nome do usuário:')
        context.user_data['action'] = 'add_name'
    elif data == 'list':
        gerenciador = context.user_data['gerenciador']
        usuarios = gerenciador.listar_usuarios()
        if usuarios:
            response = "LISTA DE USUÁRIOS:\n"
            cont = 1
            for usuario in usuarios:
                response += f"{cont} - 👥NOME: {usuario[0]}, 👁IDADE: {usuario[1]}\n"
                cont += 1
            await query.message.reply_text(response)
        else:
            await query.message.reply_text('Nenhum usuário cadastrado.')
    elif data == 'update':
        await query.message.reply_text('Digite o nome do usuário a ser atualizado:')
        context.user_data['action'] = 'update_name'
    elif data == 'delete':
        await query.message.reply_text('Digite o nome do usuário a ser excluído:')
        context.user_data['action'] = 'delete_name'

async def message(update, context):
    if update.message and update.message.text:
        text = update.message.text
        user_data = context.user_data

        if 'action' in user_data:
            action = user_data['action']
            if action == 'add_name':
                user_data['nome'] = text
                await update.message.reply_text('Digite a idade do usuário:')
                user_data['action'] = 'add_age'
            elif action == 'add_age':
                nome = user_data['nome']
                idade = text
                gerenciador = user_data['gerenciador']
                gerenciador.adicionar_usuario(nome, idade)
                await update.message.reply_text('Usuário adicionado com sucesso.')
                del user_data['action']
                del user_data['nome']
                await start(update, context)
            elif action == 'update_name':
                user_data['nome_antigo'] = text
                await update.message.reply_text('Digite o novo nome do usuário:')
                user_data['action'] = 'update_new_name'
            elif action == 'update_new_name':
                user_data['novo_nome'] = text
                await update.message.reply_text('Por favor, envie a idade do usuário para atualizá-lo.')
                user_data['action'] = 'update_age'
            elif action == 'update_age':
                novo_nome = user_data['novo_nome']
                nova_idade = text
                gerenciador = user_data['gerenciador']
                gerenciador.atualizar_usuario(user_data['nome_antigo'], novo_nome, nova_idade)
                await update.message.reply_text('Usuário atualizado com sucesso.')
                del user_data['nome_antigo']
                del user_data['novo_nome']
                del user_data['action']
                await start(update, context)
            elif action == 'delete_name':
                nome = text
                gerenciador = user_data['gerenciador']
                gerenciador.excluir_usuario(nome)
                await update.message.reply_text('Usuário excluído com sucesso.')
                del user_data['action']
                await start(update, context)
    else:
        await update.message.reply_text('Por favor, inicie o bot usando /start.')

def main():
    from TOKEN import TOKEN

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button, pattern='^add$|^list$|^update$|^delete$'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message))

    application.run_polling()

if __name__ == "__main__":
    main()
