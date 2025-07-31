import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Verificar se a API key está configurada
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY or OPENAI_API_KEY == 'sua_api_key_aqui':
    print("❌ ERRO: API Key da OpenAI não configurada!")
    print("")
    print("Para corrigir:")
    print("1. Copie o arquivo '.env.example' para '.env'")
    print("2. Edite o arquivo '.env' e substitua 'sua_api_key_aqui' pela sua chave real")
    print("3. Para obter uma API key: https://platform.openai.com/api-keys")
    print("")
    sys.exit(1)

print("✅ API Key configurada com sucesso!")
print(f"🔑 Usando API Key: {OPENAI_API_KEY[:8]}...{OPENAI_API_KEY[-4:]}")

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.etp import etp_bp
from src.routes.chat import chat_bp

# Caminho absoluto da pasta atual
basedir = os.path.abspath(os.path.dirname(__file__))

# Inicialização do app Flask
app = Flask(__name__, static_folder=os.path.join(basedir, 'static'))
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

# Configurar CORS para permitir requisições do frontend
CORS(app, origins="*")

# Registrar rotas
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(etp_bp, url_prefix='/api/etp')
app.register_blueprint(chat_bp, url_prefix='/api/chat')

# Corrigir o caminho absoluto do banco SQLite
db_path = os.path.join(basedir, 'database', 'app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar banco
db.init_app(app)
with app.app_context():
    db.create_all()

# Servir arquivos estáticos
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

# Endpoint de verificação
@app.route('/health')
def health():
    return {
        'status': 'healthy',
        'api_configured': bool(OPENAI_API_KEY),
        'version': '2.0.0'
    }

if __name__ == '__main__':
    print("🚀 Iniciando servidor ETP Sistema...")
    print(f"📍 Acesse: http://localhost:5002")
    print("🔄 Para parar o servidor: Ctrl+C")
    app.run(host='0.0.0.0', port=5002, debug=os.getenv('DEBUG', 'True').lower() == 'true')
