from datetime import datetime
from src.models.user import db
import json

class EtpSession(db.Model):
    """Modelo para sessões de geração de ETP"""
    __tablename__ = 'etp_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    # user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Removido temporariamente
    
    # Status da sessão
    status = db.Column(db.String(50), default='iniciada')  # iniciada, analisando, validando, gerando, concluida
    
    # Dados das 5 perguntas
    answers = db.Column(db.Text)  # JSON com as respostas
    answers_validated = db.Column(db.Boolean, default=False)
    
    # Preview e documento final
    preview_content = db.Column(db.Text)
    preview_approved = db.Column(db.Boolean, default=False)
    final_document_path = db.Column(db.String(500))
    
    # Metadados
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    document_analysis = db.relationship('DocumentAnalysis', backref='etp_session', lazy=True, cascade='all, delete-orphan')
    
    def get_answers(self):
        """Retorna as respostas como dicionário"""
        if self.answers:
            return json.loads(self.answers)
        return {}
    
    def set_answers(self, answers_dict):
        """Define as respostas a partir de um dicionário"""
        self.answers = json.dumps(answers_dict, ensure_ascii=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'status': self.status,
            'answers': self.get_answers(),
            'answers_validated': self.answers_validated,
            'preview_approved': self.preview_approved,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class DocumentAnalysis(db.Model):
    """Modelo para análise de documentos pré-ETP"""
    __tablename__ = 'document_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), db.ForeignKey('etp_sessions.session_id'), nullable=False)
    
    # Informações do documento
    filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)
    file_type = db.Column(db.String(50))
    file_hash = db.Column(db.String(64))
    
    # Conteúdo extraído
    extracted_content = db.Column(db.Text)
    
    # Análise da IA
    analysis_result = db.Column(db.Text)  # JSON com resultados da análise
    extracted_answers = db.Column(db.Text)  # JSON com respostas extraídas
    missing_info = db.Column(db.Text)  # JSON com informações faltantes
    
    # Status
    analysis_status = db.Column(db.String(50), default='pendente')  # pendente, processando, concluida, erro
    
    # Metadados
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    def get_analysis_result(self):
        """Retorna o resultado da análise como dicionário"""
        if self.analysis_result:
            return json.loads(self.analysis_result)
        return {}
    
    def set_analysis_result(self, result_dict):
        """Define o resultado da análise a partir de um dicionário"""
        self.analysis_result = json.dumps(result_dict, ensure_ascii=False)
    
    def get_extracted_answers(self):
        """Retorna as respostas extraídas como dicionário"""
        if self.extracted_answers:
            return json.loads(self.extracted_answers)
        return {}
    
    def set_extracted_answers(self, answers_dict):
        """Define as respostas extraídas a partir de um dicionário"""
        self.extracted_answers = json.dumps(answers_dict, ensure_ascii=False)
    
    def get_missing_info(self):
        """Retorna as informações faltantes como lista"""
        if self.missing_info:
            return json.loads(self.missing_info)
        return []
    
    def set_missing_info(self, missing_list):
        """Define as informações faltantes a partir de uma lista"""
        self.missing_info = json.dumps(missing_list, ensure_ascii=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'analysis_result': self.get_analysis_result(),
            'extracted_answers': self.get_extracted_answers(),
            'missing_info': self.get_missing_info(),
            'analysis_status': self.analysis_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }

class KnowledgeBase(db.Model):
    """Modelo para base de conhecimento (opcional)"""
    __tablename__ = 'knowledge_base'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Informações do arquivo
    filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)
    file_hash = db.Column(db.String(64), unique=True)
    
    # Conteúdo
    content = db.Column(db.Text)
    
    # Metadados
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'file_size': self.file_size,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }

class ChatSession(db.Model):
    """Modelo para sessões de chat sobre compras públicas"""
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    # user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Removido temporariamente
    
    # Histórico da conversa
    conversation_history = db.Column(db.Text)  # JSON com histórico
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Metadados
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_conversation_history(self):
        """Retorna o histórico da conversa como lista"""
        if self.conversation_history:
            return json.loads(self.conversation_history)
        return []
    
    def add_message(self, role, content):
        """Adiciona uma mensagem ao histórico"""
        history = self.get_conversation_history()
        history.append({
            'role': role,
            'content': content,
            'timestamp': datetime.utcnow().isoformat()
        })
        self.conversation_history = json.dumps(history, ensure_ascii=False)
        self.last_activity = datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'conversation_history': self.get_conversation_history(),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None
        }

class EtpTemplate(db.Model):
    """Modelo para templates de ETP"""
    __tablename__ = 'etp_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # Estrutura do template
    structure = db.Column(db.Text)  # JSON com estrutura das seções
    
    # Configurações de formatação
    formatting_config = db.Column(db.Text)  # JSON com configurações de layout
    
    # Status
    is_default = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Metadados
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_structure(self):
        """Retorna a estrutura como dicionário"""
        if self.structure:
            return json.loads(self.structure)
        return {}
    
    def set_structure(self, structure_dict):
        """Define a estrutura a partir de um dicionário"""
        self.structure = json.dumps(structure_dict, ensure_ascii=False)
    
    def get_formatting_config(self):
        """Retorna a configuração de formatação como dicionário"""
        if self.formatting_config:
            return json.loads(self.formatting_config)
        return {}
    
    def set_formatting_config(self, config_dict):
        """Define a configuração de formatação a partir de um dicionário"""
        self.formatting_config = json.dumps(config_dict, ensure_ascii=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'structure': self.get_structure(),
            'formatting_config': self.get_formatting_config(),
            'is_default': self.is_default,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

