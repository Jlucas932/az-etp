import os
import json
import hashlib
import uuid
import tempfile
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from flask_cors import cross_origin

from src.models.user import db
from src.models.etp import EtpSession, DocumentAnalysis, KnowledgeBase, ChatSession, EtpTemplate
from src.utils.document_analyzer import AdvancedDocumentAnalyzer
from src.utils.etp_generator import AdvancedEtpGenerator
from ..utils.word_formatter import ProfessionalWordFormatter
from ..utils.word_formatter_with_borders import WordFormatterWithBorders

etp_bp = Blueprint('etp', __name__)

# Configurar utilitários
openai_api_key = os.getenv('OPENAI_API_KEY')
document_analyzer = AdvancedDocumentAnalyzer(openai_api_key) if openai_api_key else None
etp_generator = AdvancedEtpGenerator(openai_api_key) if openai_api_key else None

# Perguntas do ETP conforme especificado
ETP_QUESTIONS = [
    {
        "id": 1,
        "question": "Qual a descrição da necessidade da contratação?",
        "type": "text",
        "required": True,
        "section": "OBJETO DO ESTUDO E ESPECIFICAÇÕES GERAIS"
    },
    {
        "id": 2,
        "question": "Possui demonstrativo de previsão no PCA?",
        "type": "boolean",
        "required": True,
        "section": "OBJETO DO ESTUDO E ESPECIFICAÇÕES GERAIS"
    },
    {
        "id": 3,
        "question": "Quais normas legais pretende utilizar?",
        "type": "text",
        "required": True,
        "section": "DESCRIÇÃO DOS REQUISITOS DA CONTRATAÇÃO"
    },
    {
        "id": 4,
        "question": "Qual o quantitativo e valor estimado?",
        "type": "text",
        "required": True,
        "section": "ESTIMATIVA DAS QUANTIDADES E VALORES"
    },
    {
        "id": 5,
        "question": "Haverá parcelamento da contratação?",
        "type": "boolean",
        "required": True,
        "section": "JUSTIFICATIVA PARA O PARCELAMENTO OU NÃO DA CONTRATAÇÃO"
    }
]

# Estrutura obrigatória do ETP conforme Lei 14.133/21
ETP_STRUCTURE = [
    "1. INTRODUÇÃO",
    "2. OBJETO DO ESTUDO E ESPECIFICAÇÕES GERAIS",
    "2.1 Localização da execução do objeto contratual",
    "2.2 Natureza e finalidade do objeto",
    "2.3 Classificação quanto ao sigilo",
    "2.4 Descrição da necessidade da contratação",
    "2.5 Demonstração da previsão no plano de contratações anual",
    "3. DESCRIÇÃO DOS REQUISITOS DA CONTRATAÇÃO",
    "3.1 Requisitos técnicos",
    "3.2 Requisitos de sustentabilidade",
    "3.3 Requisitos normativos e legais",
    "4. ESTIMATIVA DAS QUANTIDADES E VALORES",
    "5. LEVANTAMENTO DE MERCADO E JUSTIFICATIVA DA ESCOLHA DA SOLUÇÃO",
    "5.1 Justificativa para a escolha da solução",
    "5.2 Pesquisa de mercado",
    "6. ESTIMATIVA DO VALOR DA CONTRATAÇÃO",
    "7. DESCRIÇÃO DA SOLUÇÃO COMO UM TODO",
    "8. JUSTIFICATIVA PARA O PARCELAMENTO OU NÃO DA CONTRATAÇÃO",
    "9. DEMONSTRATIVO DOS RESULTADOS PRETENDIDOS",
    "10. PROVIDÊNCIAS ADOTADAS ANTERIORMENTE PELA ADMINISTRAÇÃO",
    "11. CONTRATAÇÕES CORRELATAS OU INTERDEPENDENTES",
    "12. AVALIAÇÃO DOS IMPACTOS AMBIENTAIS",
    "13. ANÁLISE DE RISCOS",
    "14. CONCLUSÃO E POSICIONAMENTO FINAL"
]

@etp_bp.route('/generate', methods=['POST'])
@cross_origin()
def generate():
    """Rota compatível com o frontend - inicia nova sessão ETP"""
    try:
        session_id = str(uuid.uuid4())
        
        # Criar nova sessão
        etp_session = EtpSession(
            session_id=session_id,
            status='iniciada'
        )
        
        db.session.add(etp_session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'status': 'success',
            'message': 'Sessão ETP iniciada com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Erro ao iniciar sessão: {str(e)}'
        }), 500

@etp_bp.route('/start-session', methods=['POST'])
@cross_origin()
def start_session():
    """Inicia uma nova sessão de geração de ETP"""
    try:
        session_id = str(uuid.uuid4())
        
        # Criar nova sessão
        etp_session = EtpSession(
            session_id=session_id,
            status='iniciada'
        )
        
        db.session.add(etp_session)
        db.session.commit()
        
        return jsonify({
            'session_id': session_id,
            'status': 'success',
            'message': 'Sessão iniciada com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao iniciar sessão: {str(e)}'}), 500

@etp_bp.route('/step/<int:step>', methods=['GET'])
@cross_origin()
def get_step(step):
    """Retorna conteúdo de uma etapa específica do ETP"""
    try:
        session_id = request.args.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'session_id é obrigatório'
            }), 400
        
        # Verificar se a sessão existe
        etp_session = EtpSession.query.filter_by(session_id=session_id).first()
        if not etp_session:
            return jsonify({
                'success': False,
                'error': 'Sessão não encontrada'
            }), 404
        
        # Gerar conteúdo da etapa baseado no step
        if step == 1:
            title = "Início - Informações Gerais"
            content = """
            <div class="step-content">
                <h3>Bem-vindo ao processo de geração do ETP!</h3>
                <p>Vamos começar coletando as informações básicas para seu Estudo Técnico Preliminar.</p>
                <div class="step-actions">
                    <button class="btn-primary next-btn">Continuar</button>
                </div>
            </div>
            """
        elif step == 2:
            title = "Upload de Documento (Opcional)"
            content = """
            <div class="step-content">
                <h3>Upload de Documento Pré-ETP</h3>
                <p>Se você possui um documento relacionado ao ETP, pode fazer o upload para análise automática.</p>
                <div class="upload-area">
                    <input type="file" accept=".pdf,.doc,.docx" style="display: none;">
                    <button class="upload-btn">Selecionar Arquivo</button>
                    <p>Formatos aceitos: PDF, DOC, DOCX</p>
                </div>
                <div class="step-actions">
                    <button class="btn-secondary prev-btn">Voltar</button>
                    <button class="btn-outline skip-btn">Pular Upload</button>
                    <button class="btn-primary next-btn">Continuar</button>
                </div>
            </div>
            """
        elif step == 3:
            title = "Perguntas do ETP"
            content = f"""
            <div class="step-content">
                <h3>Responda às 5 perguntas obrigatórias</h3>
                <form id="etpForm">
                    {generate_questions_html()}
                </form>
                <div class="step-actions">
                    <button class="btn-secondary prev-btn">Voltar</button>
                    <button class="btn-primary next-btn">Validar Respostas</button>
                </div>
            </div>
            """
        elif step == 4:
            title = "Validação e Preview"
            content = """
            <div class="step-content">
                <h3>Validação das Respostas</h3>
                <p>Suas respostas estão sendo validadas...</p>
                <div id="validationResults"></div>
                <div class="step-actions">
                    <button class="btn-secondary prev-btn">Voltar</button>
                    <button class="btn-primary next-btn">Gerar Preview</button>
                </div>
            </div>
            """
        elif step == 5:
            title = "Preview do Documento"
            content = """
            <div class="step-content">
                <h3>Preview do ETP</h3>
                <div id="previewContent">
                    <p>Gerando preview do documento...</p>
                </div>
                <div class="step-actions">
                    <button class="btn-secondary prev-btn">Voltar</button>
                    <button class="btn-primary next-btn">Aprovar e Gerar Documento</button>
                </div>
            </div>
            """
        elif step == 6:
            title = "Documento Final"
            content = """
            <div class="step-content">
                <h3>Documento ETP Gerado</h3>
                <p>Seu Estudo Técnico Preliminar foi gerado com sucesso!</p>
                <div class="download-area">
                    <button class="btn-success download-btn">Download do Documento</button>
                </div>
                <div class="step-actions">
                    <button class="btn-primary finish-btn">Finalizar</button>
                </div>
            </div>
            """
        else:
            return jsonify({
                'success': False,
                'error': 'Etapa inválida'
            }), 400
        
        return jsonify({
            'success': True,
            'title': title,
            'content': content,
            'step': step
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao carregar etapa: {str(e)}'
        }), 500

def generate_questions_html():
    """Gera HTML das perguntas do ETP"""
    html = ""
    for question in ETP_QUESTIONS:
        if question['type'] == 'text':
            html += f"""
            <div class="question-group">
                <label for="q{question['id']}">{question['id']}. {question['question']}</label>
                <textarea id="q{question['id']}" name="q{question['id']}" required 
                         placeholder="Digite sua resposta aqui..."></textarea>
            </div>
            """
        elif question['type'] == 'boolean':
            html += f"""
            <div class="question-group">
                <label>{question['id']}. {question['question']}</label>
                <div class="radio-group">
                    <label><input type="radio" name="q{question['id']}" value="sim" required> Sim</label>
                    <label><input type="radio" name="q{question['id']}" value="nao" required> Não</label>
                </div>
            </div>
            """
    return html

@etp_bp.route('/get-questions', methods=['GET'])
@cross_origin()
def get_questions():
    """Retorna as perguntas do ETP"""
    session_id = request.args.get('session_id')
    
    response_data = {
        'questions': ETP_QUESTIONS,
        'total': len(ETP_QUESTIONS)
    }
    
    # Se há sessão, verificar se há respostas extraídas de documento
    if session_id:
        etp_session = EtpSession.query.filter_by(session_id=session_id).first()
        if etp_session:
            # Buscar análise de documento mais recente
            doc_analysis = DocumentAnalysis.query.filter_by(
                session_id=session_id,
                analysis_status='concluida'
            ).order_by(DocumentAnalysis.processed_at.desc()).first()
            
            if doc_analysis:
                extracted_answers = doc_analysis.get_extracted_answers()
                missing_info = doc_analysis.get_missing_info()
                
                response_data['extracted_answers'] = extracted_answers
                response_data['missing_info'] = missing_info
                response_data['has_document_analysis'] = True
    
    return jsonify(response_data)

@etp_bp.route('/upload-document', methods=['POST'])
@cross_origin()
def upload_document():
    """Upload de documento para análise automática"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Nenhum arquivo enviado'
            }), 400
        
        file = request.files['file']
        session_id = request.form.get('session_id')
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Nenhum arquivo selecionado'
            }), 400
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'session_id é obrigatório'
            }), 400
        
        # Verificar se a sessão existe
        etp_session = EtpSession.query.filter_by(session_id=session_id).first()
        if not etp_session:
            return jsonify({
                'success': False,
                'error': 'Sessão não encontrada'
            }), 404
        
        # Verificar tipo de arquivo
        allowed_extensions = {'.pdf', '.doc', '.docx', '.txt'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            return jsonify({
                'success': False,
                'error': f'Tipo de arquivo não suportado. Use: {", ".join(allowed_extensions)}'
            }), 400
        
        # Salvar arquivo temporariamente e ler conteúdo
        upload_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        filename = f"{session_id}_{file.filename}"
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        # Ler conteúdo do arquivo salvo
        with open(filepath, 'rb') as f:
            file_content = f.read()
        
        # Analisar documento
        try:
            if document_analyzer:
                # Primeiro extrair o texto do arquivo
                file_extension = os.path.splitext(file.filename)[1].lower()
                document_text = document_analyzer.extract_text_from_file(file_content, file_extension)
                
                # Depois analisar o texto extraído
                analysis_result = document_analyzer.analyze_document(document_text)
                
                # Extrair respostas automaticamente do documento
                extracted_answers = document_analyzer.extract_etp_answers(analysis_result)
                
                # Salvar análise no banco
                doc_analysis = DocumentAnalysis(
                    session_id=session_id,
                    filename=file.filename,
                    file_size=len(file_content),
                    file_type=file.filename.split('.')[-1].lower(),
                    extracted_content=document_text,
                    analysis_status='concluida'
                )
                doc_analysis.set_analysis_result(analysis_result)
                
                db.session.add(doc_analysis)
                
                # Se conseguiu extrair respostas, salvar na sessão
                if extracted_answers:
                    etp_session.set_answers(extracted_answers)
                    etp_session.answers_validated = True
                    etp_session.status = 'analisado'
                
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'message': 'Documento analisado com sucesso',
                    'analysis': analysis_result,
                    'extracted_answers': extracted_answers,
                    'auto_filled': bool(extracted_answers)
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Analisador de documentos não disponível'
                }), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Erro na análise do documento: {str(e)}'
            }), 500
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Erro no upload: {str(e)}'
        }), 500

@etp_bp.route('/validate-answers', methods=['POST'])
@cross_origin()
def validate_answers():
    """Valida e salva as respostas do usuário"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        answers = data.get('answers', {})
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'session_id é obrigatório'
            }), 400
        
        # Verificar se a sessão existe
        etp_session = EtpSession.query.filter_by(session_id=session_id).first()
        if not etp_session:
            return jsonify({
                'success': False,
                'error': 'Sessão não encontrada'
            }), 404
        
        # Validar se todas as perguntas obrigatórias foram respondidas
        missing_questions = []
        for question in ETP_QUESTIONS:
            if question['required'] and str(question['id']) not in answers:
                missing_questions.append(question['question'])
        
        if missing_questions:
            return jsonify({
                'success': False,
                'error': 'Perguntas obrigatórias não respondidas',
                'missing_questions': missing_questions
            }), 400
        
        # Salvar respostas
        etp_session.set_answers(answers)
        etp_session.answers_validated = True
        etp_session.status = 'validando'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Respostas validadas com sucesso',
            'answers': answers,
            'status': 'validated'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Erro ao validar respostas: {str(e)}'
        }), 500

@etp_bp.route('/generate-preview', methods=['POST'])
@cross_origin()
def generate_preview():
    """Gera preview textual completo do ETP"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'session_id é obrigatório'
            }), 400
        
        # Verificar se a sessão existe
        etp_session = EtpSession.query.filter_by(session_id=session_id).first()
        if not etp_session:
            return jsonify({
                'success': False,
                'error': 'Sessão não encontrada'
            }), 404
        
        if not etp_session.answers_validated:
            return jsonify({
                'success': False,
                'error': 'Respostas devem ser validadas primeiro'
            }), 400
        
        # Preparar dados da sessão
        session_data = {
            'answers': etp_session.get_answers(),
            'session_id': session_id
        }
        
        # Preparar dados de contexto
        context_data = {}
        
        # Adicionar análise de documento se disponível
        try:
            doc_analysis = DocumentAnalysis.query.filter_by(
                session_id=session_id,
                analysis_status='concluida'
            ).order_by(DocumentAnalysis.processed_at.desc()).first()
            
            if doc_analysis:
                context_data['document_analysis'] = {
                    'filename': doc_analysis.filename,
                    'extracted_content': doc_analysis.extracted_content,
                    'analysis_result': doc_analysis.get_analysis_result()
                }
        except Exception as e:
            print(f"Erro ao buscar análise de documento: {e}")
        
        # Gerar preview usando gerador avançado
        try:
            if etp_generator:
                # Versão otimizada para preview rápido
                preview_content = etp_generator.generate_quick_preview(
                    session_data, 
                    context_data
                )
            else:
                # Fallback simples e rápido
                answers = session_data['answers']
                preview_content = f"""ESTUDO TÉCNICO PRELIMINAR

1. DESCRIÇÃO DA NECESSIDADE DA CONTRATAÇÃO:
{answers.get('1', 'Não informado')}

2. DEMONSTRATIVO DE PREVISÃO NO PCA:
{answers.get('2', 'Não informado')}

3. NORMAS LEGAIS APLICÁVEIS:
{answers.get('3', 'Não informado')}

4. QUANTITATIVO E VALOR ESTIMADO:
{answers.get('4', 'Não informado')}

5. PARCELAMENTO DA CONTRATAÇÃO:
{answers.get('5', 'Não informado')}

Este é um preview simplificado. O documento final conterá formatação profissional e seções detalhadas conforme Lei 14.133/21."""
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Erro na geração do preview: {str(e)}'
            }), 500
        
        # Salvar preview
        etp_session.preview_content = preview_content
        etp_session.status = 'preview_gerado'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'preview': preview_content,
            'status': 'generated',
            'message': 'Preview gerado com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Erro ao gerar preview: {str(e)}'
        }), 500

@etp_bp.route('/download-document/<filename>', methods=['GET'])
@cross_origin()
def download_document_by_filename(filename):
    """Download do documento ETP gerado"""
    try:
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)
        
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': 'Arquivo não encontrado'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Erro ao baixar arquivo: {str(e)}'}), 500

@etp_bp.route('/session-status/<session_id>', methods=['GET'])
@cross_origin()
def get_session_status(session_id):
    """Retorna o status da sessão"""
    try:
        etp_session = EtpSession.query.filter_by(session_id=session_id).first()
        if not etp_session:
            return jsonify({'error': 'Sessão não encontrada'}), 404
        
        return jsonify(etp_session.to_dict())
        
    except Exception as e:
        return jsonify({'error': f'Erro ao obter status: {str(e)}'}), 500

# Funções auxiliares

def extract_text_from_file(file_content, file_ext):
    """Extrai texto de diferentes tipos de arquivo"""
    try:
        if file_ext == '.pdf':
            # Usar PyPDF2 para PDFs
            import io
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        
        elif file_ext in ['.doc', '.docx']:
            # Usar python-docx para documentos Word
            import io
            doc_file = io.BytesIO(file_content)
            doc = Document(doc_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        
        else:
            return "Tipo de arquivo não suportado para extração de texto"
            
    except Exception as e:
        return f"Erro ao extrair texto: {str(e)}"

def analyze_document_with_ai(document_text):
    """Analisa documento usando IA para extrair respostas"""
    try:
        client = openai.OpenAI(api_key=openai.api_key)
        
        prompt = f"""
        Analise o documento fornecido e tente extrair informações que respondam às seguintes perguntas do ETP:

        1. Qual a descrição da necessidade da contratação?
        2. Possui demonstrativo de previsão no PCA?
        3. Quais normas legais pretende utilizar?
        4. Qual o quantitativo e valor estimado?
        5. Haverá parcelamento da contratação?

        DOCUMENTO:
        {document_text[:4000]}  # Limitar para não exceder tokens

        Retorne um JSON com:
        - extracted_answers: dict com as respostas encontradas (chave: número da pergunta, valor: resposta)
        - missing_info: lista com números das perguntas que não puderam ser respondidas
        - confidence: dict com nível de confiança para cada resposta (0-1)

        Seja preciso e indique claramente quando uma informação não foi encontrada.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um especialista em análise de documentos de licitação e ETP. Analise documentos e extraia informações específicas de forma precisa."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.1
        )
        
        # Tentar parsear a resposta como JSON
        try:
            result = json.loads(response.choices[0].message.content)
        except:
            # Se não conseguir parsear, criar estrutura padrão
            result = {
                "extracted_answers": {},
                "missing_info": [1, 2, 3, 4, 5],
                "confidence": {},
                "raw_response": response.choices[0].message.content
            }
        
        return result
        
    except Exception as e:
        return {
            "extracted_answers": {},
            "missing_info": [1, 2, 3, 4, 5],
            "confidence": {},
            "error": str(e)
        }

def generate_etp_content_with_ai(etp_session, is_preview=False):
    """Gera conteúdo do ETP usando IA"""
    try:
        client = openai.OpenAI(api_key=openai.api_key)
        
        answers = etp_session.get_answers()
        
        # Construir contexto
        context = build_context_for_generation(etp_session)
        
        prompt_type = "prévia detalhada" if is_preview else "versão final"
        
        prompt = f"""
        Gere uma {prompt_type} de um Estudo Técnico Preliminar (ETP) seguindo rigorosamente a Lei 14.133/21.

        ESTRUTURA OBRIGATÓRIA:
        {chr(10).join(ETP_STRUCTURE)}

        INSTRUÇÕES IMPORTANTES:
        1. Siga FIELMENTE a estrutura obrigatória acima
        2. Cada seção deve ter entre 8-10 parágrafos bem elaborados
        3. Use linguagem administrativa clara, completa, formal e legal
        4. Garanta conformidade total com a Lei 14.133/21
        5. Inclua tabelas quando apropriado (seções 4, 6, 13)
        6. Mantenha consistência técnica e formal

        CONTEXTO E RESPOSTAS:
        {context}

        Gere o ETP completo seguindo a estrutura obrigatória:
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um especialista em licitações públicas e elaboração de Estudos Técnicos Preliminares conforme a Lei 14.133/21. Gere documentos técnicos completos, detalhados e em conformidade legal."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.2
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        raise Exception(f"Erro na geração de conteúdo: {str(e)}")

def build_context_for_generation(etp_session):
    """Constrói contexto para geração do ETP"""
    context = "INFORMAÇÕES PARA GERAÇÃO DO ETP:\n\n"
    
    # Adicionar respostas do usuário
    answers = etp_session.get_answers()
    context += "RESPOSTAS DO USUÁRIO:\n"
    for i, question in enumerate(ETP_QUESTIONS, 1):
        answer = answers.get(str(i), "Não informado")
        context += f"{i}. {question['question']}\n"
        context += f"Resposta: {answer}\n\n"
    
    # Adicionar análise de documento se disponível
    doc_analysis = DocumentAnalysis.query.filter_by(
        session_id=etp_session.session_id,
        analysis_status='concluida'
    ).order_by(DocumentAnalysis.processed_at.desc()).first()
    
    if doc_analysis and doc_analysis.extracted_content:
        context += "DOCUMENTO DE REFERÊNCIA ANALISADO:\n"
        context += doc_analysis.extracted_content[:2000]  # Limitar tamanho
        context += "\n\n"
    
    # Adicionar base de conhecimento se disponível
    kb_files = KnowledgeBase.query.filter_by(is_active=True).limit(3).all()
    if kb_files:
        context += "BASE DE CONHECIMENTO (Modelos de referência):\n"
        for kb_file in kb_files:
            context += f"--- {kb_file.filename} ---\n"
            context += kb_file.content[:1500]  # Limitar para não exceder tokens
            context += "\n\n"
    
    return context

def adjust_preview_with_feedback(etp_session, feedback):
    """Ajusta o preview com base no feedback do usuário"""
    try:
        client = openai.OpenAI(api_key=openai.api_key)
        
        current_preview = etp_session.preview_content
        
        prompt = f"""
        Ajuste o seguinte ETP com base no feedback fornecido pelo usuário:

        FEEDBACK DO USUÁRIO:
        {feedback}

        ETP ATUAL:
        {current_preview}

        Faça os ajustes solicitados mantendo:
        1. A estrutura obrigatória da Lei 14.133/21
        2. A qualidade técnica e formal
        3. A conformidade legal
        4. A coerência do documento

        Retorne o ETP ajustado:
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um especialista em revisão e ajuste de documentos de ETP. Faça ajustes precisos mantendo a qualidade e conformidade legal."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.2
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        # Se houver erro, retornar o preview original
        return etp_session.preview_content

def create_professional_word_document(etp_session):
    """Cria documento Word com formatação profissional"""
    try:
        doc = Document()
        
        # Configurar margens (2,5cm superior/inferior, 3cm esquerda/direita)
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(0.98)  # 2,5cm
            section.bottom_margin = Inches(0.98)  # 2,5cm
            section.left_margin = Inches(1.18)  # 3cm
            section.right_margin = Inches(1.18)  # 3cm
        
        # Criar estilos personalizados
        create_custom_styles(doc)
        
        # Adicionar cabeçalho
        add_header(doc)
        
        # Título principal
        title = doc.add_heading('ESTUDO TÉCNICO PRELIMINAR (ETP)', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Adicionar data
        date_para = doc.add_paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y')}")
        date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_paragraph("")  # Espaço
        
        # Processar conteúdo do preview
        content = etp_session.preview_content
        process_content_with_formatting(doc, content)
        
        # Adicionar rodapé
        add_footer(doc)
        
        # Salvar documento
        temp_dir = tempfile.gettempdir()
        doc_filename = f"ETP_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        doc_path = os.path.join(temp_dir, doc_filename)
        doc.save(doc_path)
        
        return doc_path
        
    except Exception as e:
        raise Exception(f"Erro ao criar documento Word: {str(e)}")

def create_custom_styles(doc):
    """Cria estilos personalizados para o documento"""
    styles = doc.styles
    
    # Estilo para títulos principais (com fundo azul)
    if 'Titulo Principal' not in [s.name for s in styles]:
        title_style = styles.add_style('Titulo Principal', WD_STYLE_TYPE.PARAGRAPH)
        title_format = title_style.paragraph_format
        title_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        title_format.space_before = Pt(12)
        title_format.space_after = Pt(12)
        
        title_font = title_style.font
        title_font.name = 'Arial'
        title_font.size = Pt(14)
        title_font.bold = True
        title_font.color.rgb = RGBColor(255, 255, 255)  # Branco
    
    # Estilo para subtítulos
    if 'Subtitulo' not in [s.name for s in styles]:
        subtitle_style = styles.add_style('Subtitulo', WD_STYLE_TYPE.PARAGRAPH)
        subtitle_format = subtitle_style.paragraph_format
        subtitle_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        subtitle_format.space_before = Pt(6)
        subtitle_format.space_after = Pt(6)
        
        subtitle_font = subtitle_style.font
        subtitle_font.name = 'Arial'
        subtitle_font.size = Pt(12)
        subtitle_font.bold = True
    
    # Estilo para corpo do texto
    if 'Corpo Texto' not in [s.name for s in styles]:
        body_style = styles.add_style('Corpo Texto', WD_STYLE_TYPE.PARAGRAPH)
        body_format = body_style.paragraph_format
        body_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        body_format.line_spacing = 1.5
        body_format.first_line_indent = Inches(0.49)  # 1,25cm
        
        body_font = body_style.font
        body_font.name = 'Arial'
        body_font.size = Pt(12)

def add_header(doc):
    """Adiciona cabeçalho institucional"""
    header = doc.sections[0].header
    header_para = header.paragraphs[0]
    header_para.text = "GOVERNO DO ESTADO\nSECRETARIA DE ADMINISTRAÇÃO\nESTUDO TÉCNICO PRELIMINAR"
    header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

def add_footer(doc):
    """Adiciona rodapé com numeração"""
    footer = doc.sections[0].footer
    footer_para = footer.paragraphs[0]
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Adicionar numeração de página
    run = footer_para.runs[0] if footer_para.runs else footer_para.add_run()
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    run._element.append(fldChar1)
    
    instrText = OxmlElement('w:instrText')
    instrText.text = "PAGE"
    run._element.append(instrText)
    
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'end')
    run._element.append(fldChar2)

def process_content_with_formatting(doc, content):
    """Processa o conteúdo aplicando formatação adequada"""
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Identificar tipo de linha e aplicar formatação
        if line.upper().startswith(tuple([f"{i}." for i in range(1, 15)])) and line.isupper():
            # Título principal
            para = doc.add_paragraph(line, style='Titulo Principal')
            # Adicionar fundo azul escuro
            add_blue_background(para)
        
        elif any(line.startswith(f"{i}.{j}") for i in range(1, 15) for j in range(1, 10)):
            # Subtítulo
            doc.add_paragraph(line, style='Subtitulo')
        
        else:
            # Corpo do texto
            doc.add_paragraph(line, style='Corpo Texto')

def add_blue_background(paragraph):
    """Adiciona fundo azul escuro ao parágrafo"""
    try:
        # Configurar sombreamento azul escuro
        shading_elm = OxmlElement('w:shd')
        shading_elm.set(qn('w:val'), 'clear')
        shading_elm.set(qn('w:color'), 'auto')
        shading_elm.set(qn('w:fill'), '1f4e79')  # Azul escuro
        paragraph._element.get_or_add_pPr().append(shading_elm)
    except:
        pass  # Se não conseguir aplicar, continuar sem o fundo


@etp_bp.route('/get-preview', methods=['POST'])
@cross_origin()
def get_preview():
    """Busca preview salvo da sessão"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'session_id é obrigatório'
            }), 400
        
        # Buscar sessão
        etp_session = EtpSession.query.filter_by(session_id=session_id).first()
        if not etp_session:
            return jsonify({
                'success': False,
                'error': 'Sessão não encontrada'
            }), 404
        
        if not etp_session.preview_content:
            return jsonify({
                'success': False,
                'error': 'Preview não encontrado. Gere o preview primeiro.'
            }), 404
        
        return jsonify({
            'success': True,
            'preview': etp_session.preview_content,
            'status': etp_session.status
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao buscar preview: {str(e)}'
        }), 500

@etp_bp.route('/approve-preview', methods=['POST'])
@cross_origin()
def approve_preview():
    """Aprova o preview para geração do documento final"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'session_id é obrigatório'
            }), 400
        
        # Buscar sessão
        etp_session = EtpSession.query.filter_by(session_id=session_id).first()
        if not etp_session:
            return jsonify({
                'success': False,
                'error': 'Sessão não encontrada'
            }), 404
        
        if not etp_session.preview_content:
            return jsonify({
                'success': False,
                'error': 'Preview deve ser gerado primeiro'
            }), 400
        
        # Marcar como aprovado
        etp_session.status = 'aprovado'
        etp_session.approved_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Preview aprovado com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Erro ao aprovar preview: {str(e)}'
        }), 500

@etp_bp.route('/generate-final', methods=['POST'])
@cross_origin()
def generate_final():
    """Gera documento Word final"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'session_id é obrigatório'
            }), 400
        
        # Buscar sessão
        etp_session = EtpSession.query.filter_by(session_id=session_id).first()
        if not etp_session:
            return jsonify({
                'success': False,
                'error': 'Sessão não encontrada'
            }), 404
        
        if etp_session.status != 'aprovado':
            return jsonify({
                'success': False,
                'error': 'Preview deve ser aprovado primeiro'
            }), 400
        
        # Gerar documento Word usando o preview aprovado
        try:
            # Usar formatador com bordas baseado no modelo da concorrência
            word_formatter = WordFormatterWithBorders()
            
            # Preparar dados para o documento
            document_data = {
                'title': 'Estudo Técnico Preliminar',
                'content': etp_session.preview_content,
                'answers': etp_session.get_answers(),
                'session_id': session_id,
                'generated_at': datetime.utcnow().strftime('%d/%m/%Y %H:%M')
            }
            
            # Gerar arquivo Word com bordas e formatação profissional
            word_file_path = word_formatter.create_etp_with_borders(
                etp_session.preview_content, 
                document_data
            )       
            # Salvar caminho do arquivo na sessão
            etp_session.final_document_path = word_file_path
            etp_session.status = 'concluido'
            etp_session.completed_at = datetime.utcnow()
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Documento Word gerado com sucesso',
                'download_url': f'/api/etp/download/{session_id}'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Erro na geração do documento: {str(e)}'
            }), 500
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Erro ao gerar documento final: {str(e)}'
        }), 500

@etp_bp.route('/download/<session_id>', methods=['GET'])
@cross_origin()
def download_document(session_id):
    """Download do documento Word gerado"""
    try:
        # Buscar sessão
        etp_session = EtpSession.query.filter_by(session_id=session_id).first()
        if not etp_session:
            return jsonify({'error': 'Sessão não encontrada'}), 404
        
        if not etp_session.final_document_path:
            return jsonify({'error': 'Documento não encontrado'}), 404
        
        # Verificar se arquivo existe
        if not os.path.exists(etp_session.final_document_path):
            return jsonify({'error': 'Arquivo não encontrado no servidor'}), 404
        
        # Enviar arquivo
        return send_file(
            etp_session.final_document_path,
            as_attachment=True,
            download_name=f'ETP_{session_id[:8]}.docx',
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        return jsonify({'error': f'Erro no download: {str(e)}'}), 500

