import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import openai

from src.models.user import db
from src.models.etp import ChatSession

chat_bp = Blueprint('chat', __name__)

# Configurar a API key da OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Tópicos permitidos no chat
ALLOWED_TOPICS = [
    'compras públicas',
    'licitações',
    'termo de referência',
    'etp',
    'estudo técnico preliminar',
    'lei 14.133/21',
    'lei 14133',
    'pregão eletrônico',
    'concorrência',
    'dispensa',
    'inexigibilidade',
    'modalidades de licitação',
    'contratos públicos',
    'administração pública',
    'tribunal de contas',
    'controle interno',
    'fiscalização',
    'penalidades',
    'sanções administrativas',
    'registro de preços',
    'ata de registro de preços',
    'sistema de registro de preços',
    'pncp',
    'portal nacional de contratações públicas',
    'comprasnet',
    'fornecedores',
    'habilitação',
    'qualificação técnica',
    'proposta comercial',
    'julgamento',
    'recursos administrativos',
    'impugnação',
    'sustentabilidade',
    'critérios de sustentabilidade',
    'margem de preferência',
    'micro e pequenas empresas',
    'cooperativas',
    'agricultura familiar'
]

# Palavras-chave que indicam tópicos não permitidos
FORBIDDEN_KEYWORDS = [
    'receita culinária',
    'receita de bolo',
    'como cozinhar',
    'futebol',
    'esporte',
    'filme',
    'música',
    'entretenimento',
    'relacionamento',
    'amor',
    'namoro',
    'casamento',
    'viagem',
    'turismo',
    'medicina',
    'saúde',
    'doença',
    'remédio',
    'tratamento médico',
    'programação',
    'código',
    'python',
    'javascript',
    'html',
    'css',
    'banco de dados',
    'inteligência artificial',
    'machine learning',
    'deep learning'
]

@chat_bp.route('/start-chat', methods=['POST'])
@cross_origin()
def start_chat():
    """Inicia uma nova sessão de chat"""
    try:
        session_id = str(uuid.uuid4())
        
        # Criar nova sessão de chat
        chat_session = ChatSession(
            session_id=session_id,
            is_active=True
        )
        
        # Adicionar mensagem de boas-vindas
        welcome_message = """Olá! Sou seu assistente especializado em compras públicas e licitações.

Posso ajudá-lo com dúvidas sobre:
• Lei 14.133/21 (Nova Lei de Licitações)
• Modalidades de licitação (pregão, concorrência, etc.)
• Elaboração de Termo de Referência e ETP
• Procedimentos de contratação pública
• Contratos administrativos
• Fiscalização e controle
• Portal Nacional de Contratações Públicas (PNCP)
• Sustentabilidade em compras públicas
• E muito mais sobre o tema!

Como posso ajudá-lo hoje?"""
        
        chat_session.add_message('assistant', welcome_message)
        
        db.session.add(chat_session)
        db.session.commit()
        
        return jsonify({
            'session_id': session_id,
            'welcome_message': welcome_message,
            'status': 'success'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao iniciar chat: {str(e)}'}), 500

@chat_bp.route('/message', methods=['POST'])
@cross_origin()
def message():
    """Rota compatível com o frontend - envia mensagem no chat"""
    try:
        # Verificar se há dados JSON válidos
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type deve ser application/json'
            }), 400
        
        try:
            data = request.get_json()
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'JSON inválido: {str(e)}'
            }), 400
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados JSON não fornecidos'
            }), 400
        
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Mensagem é obrigatória'
            }), 400
        
        # Se não há session_id, criar uma nova sessão
        if not session_id:
            session_id = str(uuid.uuid4())
            chat_session = ChatSession(
                session_id=session_id,
                is_active=True
            )
            db.session.add(chat_session)
        else:
            chat_session = ChatSession.query.filter_by(session_id=session_id, is_active=True).first()
            if not chat_session:
                # Criar nova sessão se não encontrar
                chat_session = ChatSession(
                    session_id=session_id,
                    is_active=True
                )
                db.session.add(chat_session)
        
        # Verificar se o tópico é permitido
        topic_check = check_topic_allowed(user_message)
        if not topic_check['allowed']:
            response_message = f"""Desculpe, mas só posso responder perguntas relacionadas a compras públicas e licitações.

{topic_check['reason']}

Que tal me perguntar sobre:
• Como elaborar um Termo de Referência?
• Quais são as modalidades de licitação da Lei 14.133/21?
• Como funciona o pregão eletrônico?
• Critérios de sustentabilidade em compras públicas?
• Procedimentos de fiscalização contratual?"""
        else:
            # Gerar resposta usando IA
            try:
                response_message = generate_chat_response(chat_session, user_message)
            except Exception as e:
                response_message = f"Desculpe, ocorreu um erro ao processar sua pergunta. Tente novamente.\n\nDetalhes técnicos: {str(e)}"
        
        # Salvar mensagens
        try:
            chat_session.add_message('user', user_message)
            chat_session.add_message('assistant', response_message)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': f'Erro ao salvar mensagens: {str(e)}'
            }), 500
        
        return jsonify({
            'success': True,
            'response': response_message,
            'session_id': session_id,
            'topic_allowed': topic_check['allowed']
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Erro interno do servidor: {str(e)}'
        }), 500

@chat_bp.route('/send-message', methods=['POST'])
@cross_origin()
def send_message():
    """Envia mensagem no chat"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        message = data.get('message', '').strip()
        
        if not session_id or not message:
            return jsonify({'error': 'session_id e message são obrigatórios'}), 400
        
        # Verificar se a sessão existe
        chat_session = ChatSession.query.filter_by(session_id=session_id, is_active=True).first()
        if not chat_session:
            return jsonify({'error': 'Sessão de chat não encontrada'}), 404
        
        # Verificar se o tópico é permitido
        topic_check = check_topic_allowed(message)
        if not topic_check['allowed']:
            response_message = f"""Desculpe, mas só posso responder perguntas relacionadas a compras públicas e licitações.

{topic_check['reason']}

Que tal me perguntar sobre:
• Como elaborar um Termo de Referência?
• Quais são as modalidades de licitação da Lei 14.133/21?
• Como funciona o pregão eletrônico?
• Critérios de sustentabilidade em compras públicas?
• Procedimentos de fiscalização contratual?"""
            
            # Salvar mensagens
            chat_session.add_message('user', message)
            chat_session.add_message('assistant', response_message)
            db.session.commit()
            
            return jsonify({
                'response': response_message,
                'topic_allowed': False,
                'status': 'success'
            })
        
        # Gerar resposta usando IA
        ai_response = generate_chat_response(chat_session, message)
        
        # Salvar mensagens
        chat_session.add_message('user', message)
        chat_session.add_message('assistant', ai_response)
        
        db.session.commit()
        
        return jsonify({
            'response': ai_response,
            'topic_allowed': True,
            'status': 'success'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao processar mensagem: {str(e)}'}), 500

@chat_bp.route('/get-history/<session_id>', methods=['GET'])
@cross_origin()
def get_chat_history(session_id):
    """Retorna o histórico da conversa"""
    try:
        chat_session = ChatSession.query.filter_by(session_id=session_id, is_active=True).first()
        if not chat_session:
            return jsonify({'error': 'Sessão de chat não encontrada'}), 404
        
        return jsonify({
            'history': chat_session.get_conversation_history(),
            'session_info': chat_session.to_dict(),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao obter histórico: {str(e)}'}), 500

@chat_bp.route('/end-chat', methods=['POST'])
@cross_origin()
def end_chat():
    """Encerra uma sessão de chat"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'error': 'session_id é obrigatório'}), 400
        
        chat_session = ChatSession.query.filter_by(session_id=session_id).first()
        if not chat_session:
            return jsonify({'error': 'Sessão de chat não encontrada'}), 404
        
        chat_session.is_active = False
        db.session.commit()
        
        return jsonify({
            'message': 'Chat encerrado com sucesso',
            'status': 'success'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao encerrar chat: {str(e)}'}), 500

@chat_bp.route('/clear-history', methods=['POST'])
@cross_origin()
def clear_chat_history():
    """Limpa o histórico de uma sessão de chat"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'error': 'session_id é obrigatório'}), 400
        
        chat_session = ChatSession.query.filter_by(session_id=session_id).first()
        if not chat_session:
            return jsonify({'error': 'Sessão de chat não encontrada'}), 404
        
        # Limpar histórico mantendo apenas mensagem de boas-vindas
        welcome_message = """Olá! Sou seu assistente especializado em compras públicas e licitações.

Posso ajudá-lo com dúvidas sobre:
• Lei 14.133/21 (Nova Lei de Licitações)
• Modalidades de licitação (pregão, concorrência, etc.)
• Elaboração de Termo de Referência e ETP
• Procedimentos de contratação pública
• Contratos administrativos
• Fiscalização e controle
• Portal Nacional de Contratações Públicas (PNCP)
• Sustentabilidade em compras públicas
• E muito mais sobre o tema!

Como posso ajudá-lo hoje?"""
        
        chat_session.conversation_history = None
        chat_session.add_message('assistant', welcome_message)
        chat_session.last_activity = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Histórico limpo com sucesso',
            'welcome_message': welcome_message,
            'status': 'success'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao limpar histórico: {str(e)}'}), 500

# Funções auxiliares

def check_topic_allowed(message):
    """Verifica se o tópico da mensagem é permitido"""
    message_lower = message.lower()
    
    # Verificar palavras-chave proibidas
    for forbidden in FORBIDDEN_KEYWORDS:
        if forbidden in message_lower:
            return {
                'allowed': False,
                'reason': 'Sua pergunta parece estar fora do escopo de compras públicas e licitações.'
            }
    
    # Verificar se contém tópicos permitidos
    has_allowed_topic = False
    for topic in ALLOWED_TOPICS:
        if topic in message_lower:
            has_allowed_topic = True
            break
    
    # Se não encontrou tópicos específicos, usar análise mais flexível
    if not has_allowed_topic:
        # Palavras que podem indicar contexto de compras públicas
        context_words = [
            'contrat', 'licit', 'compra', 'aquisi', 'fornec', 'serviç',
            'obra', 'público', 'administra', 'governo', 'estado', 'município',
            'edital', 'proposta', 'orçamento', 'preço', 'valor', 'custo',
            'fiscal', 'controle', 'auditoria', 'tribunal', 'tcu', 'cgu',
            'transparência', 'portal', 'sistema', 'registro', 'ata',
            'penalidade', 'sanção', 'multa', 'rescisão', 'aditivo'
        ]
        
        for word in context_words:
            if word in message_lower:
                has_allowed_topic = True
                break
    
    if has_allowed_topic:
        return {'allowed': True, 'reason': ''}
    else:
        return {
            'allowed': False,
            'reason': 'Não identifiquei sua pergunta como relacionada a compras públicas ou licitações.'
        }

def generate_chat_response(chat_session, user_message):
    """Gera resposta do chat usando IA"""
    try:
        client = openai.OpenAI(api_key=openai.api_key)
        
        # Construir histórico da conversa
        conversation_history = chat_session.get_conversation_history()
        
        # Preparar mensagens para a IA
        messages = [
            {
                "role": "system",
                "content": """Você é um assistente especializado em compras públicas e licitações no Brasil.

INSTRUÇÕES IMPORTANTES:
1. Responda APENAS sobre tópicos relacionados a compras públicas, licitações e administração pública
2. Base suas respostas na Lei 14.133/21 (Nova Lei de Licitações) e legislação correlata
3. Seja preciso, técnico e didático
4. Cite artigos da lei quando relevante
5. Forneça exemplos práticos quando possível
6. Mantenha linguagem profissional mas acessível
7. Se não souber algo específico, seja honesto e sugira consultar a legislação

TÓPICOS QUE VOCÊ PODE ABORDAR:
- Lei 14.133/21 e suas aplicações
- Modalidades de licitação (pregão, concorrência, etc.)
- Elaboração de Termo de Referência e ETP
- Contratos administrativos
- Fiscalização e controle
- PNCP (Portal Nacional de Contratações Públicas)
- Sustentabilidade em compras públicas
- Procedimentos administrativos
- Recursos e impugnações
- Penalidades e sanções
- Registro de preços
- Habilitação e qualificação
- Critérios de julgamento

Seja sempre útil e educativo em suas respostas."""
            }
        ]
        
        # Adicionar histórico recente (últimas 10 mensagens)
        recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
        for msg in recent_history[:-1]:  # Excluir a última (que é a atual)
            messages.append({
                "role": msg['role'],
                "content": msg['content']
            })
        
        # Adicionar mensagem atual
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Modelo mais estável
            messages=messages,
            max_tokens=800,  # Reduzido para resposta mais rápida
            temperature=0.1  # Reduzido para resposta mais focada e rápida
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Desculpe, ocorreu um erro ao processar sua pergunta. Tente novamente em alguns instantes.\n\nErro técnico: {str(e)}"

@chat_bp.route('/get-topics', methods=['GET'])
@cross_origin()
def get_allowed_topics():
    """Retorna lista de tópicos permitidos"""
    return jsonify({
        'allowed_topics': ALLOWED_TOPICS,
        'examples': [
            "Como elaborar um Termo de Referência?",
            "Quais são as modalidades de licitação da Lei 14.133/21?",
            "Como funciona o pregão eletrônico?",
            "Quais são os critérios de sustentabilidade obrigatórios?",
            "Como fazer a fiscalização de contratos?",
            "O que é o PNCP e como utilizá-lo?",
            "Quais são as penalidades previstas na lei?",
            "Como funciona o sistema de registro de preços?"
        ],
        'status': 'success'
    })

