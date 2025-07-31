from flask import Blueprint, request, jsonify, session
import time
import json
from datetime import datetime
from ..utils.etp_generator_optimized import OptimizedEtpGenerator
from ..utils.etp_generator import AdvancedEtpGenerator
import os

etp_optimized_bp = Blueprint('etp_optimized', __name__)

def get_etp_generator(use_optimized=True):
    """Retorna gerador otimizado ou original baseado na configuração"""
    api_key = os.getenv('OPENAI_API_KEY')
    
    if use_optimized:
        try:
            return OptimizedEtpGenerator(api_key)
        except Exception as e:
            print(f"Fallback para gerador original: {e}")
            return AdvancedEtpGenerator(api_key)
    else:
        return AdvancedEtpGenerator(api_key)

@etp_optimized_bp.route('/generate-preview-fast', methods=['POST'])
def generate_preview_fast():
    """Endpoint otimizado para geração rápida de preview"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        use_optimized = data.get('use_optimized', True)
        
        if not session_id:
            return jsonify({'error': 'Session ID é obrigatório'}), 400
        
        # Recuperar dados da sessão
        session_data = session.get(f'etp_data_{session_id}', {})
        
        if not session_data.get('answers'):
            return jsonify({'error': 'Dados da sessão não encontrados'}), 404
        
        # Medir tempo de geração
        start_time = time.time()
        
        # Usar gerador apropriado
        generator = get_etp_generator(use_optimized)
        
        if use_optimized and hasattr(generator, 'generate_ultra_fast_preview'):
            preview = generator.generate_ultra_fast_preview(session_data)
            generator_used = "optimized"
        else:
            preview = generator.generate_quick_preview(session_data)
            generator_used = "original"
        
        generation_time = time.time() - start_time
        
        # Validar completude se possível
        sections_found = 0
        for i in range(1, 15):
            if f"{i}." in preview:
                sections_found += 1
        
        is_complete = sections_found >= 12  # Pelo menos 12 das 14 seções
        
        return jsonify({
            'success': True,
            'preview': preview,
            'metadata': {
                'generator_used': generator_used,
                'generation_time': round(generation_time, 2),
                'content_size': len(preview),
                'sections_found': sections_found,
                'is_complete': is_complete,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro na geração do preview: {str(e)}'
        }), 500

@etp_optimized_bp.route('/generate-complete-fast', methods=['POST'])
def generate_complete_fast():
    """Endpoint otimizado para geração completa de ETP"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        use_optimized = data.get('use_optimized', True)
        
        if not session_id:
            return jsonify({'error': 'Session ID é obrigatório'}), 400
        
        # Recuperar dados da sessão
        session_data = session.get(f'etp_data_{session_id}', {})
        
        if not session_data.get('answers'):
            return jsonify({'error': 'Dados da sessão não encontrados'}), 404
        
        # Medir tempo de geração
        start_time = time.time()
        
        # Usar gerador apropriado
        generator = get_etp_generator(use_optimized)
        
        if use_optimized and hasattr(generator, 'generate_complete_etp_optimized'):
            etp_content = generator.generate_complete_etp_optimized(session_data, is_preview=False)
            generator_used = "optimized"
        else:
            etp_content = generator.generate_complete_etp(session_data, is_preview=False)
            generator_used = "original"
        
        generation_time = time.time() - start_time
        
        # Validar completude
        validation = {}
        if hasattr(generator, 'validate_etp_completeness'):
            validation = generator.validate_etp_completeness(etp_content)
        
        return jsonify({
            'success': True,
            'etp_content': etp_content,
            'metadata': {
                'generator_used': generator_used,
                'generation_time': round(generation_time, 2),
                'content_size': len(etp_content),
                'validation': validation,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro na geração do ETP: {str(e)}'
        }), 500

@etp_optimized_bp.route('/performance-test', methods=['POST'])
def performance_test():
    """Endpoint para teste de performance comparativo"""
    try:
        data = request.get_json()
        test_type = data.get('test_type', 'preview')  # 'preview' ou 'complete'
        
        # Dados de teste
        test_session_data = {
            'answers': {
                '1': 'Contratação de sistema de gestão de documentos eletrônicos',
                '2': 'Sim, previsto no PCA 2024',
                '3': 'Lei 14.133/2021, Decreto 10.024/2019',
                '4': 'R$ 150.000,00 para licenças e R$ 50.000,00 para implantação',
                '5': 'Não haverá parcelamento'
            },
            'session_id': 'performance_test'
        }
        
        results = {}
        
        # Teste com gerador original
        try:
            original_generator = AdvancedEtpGenerator(os.getenv('OPENAI_API_KEY'))
            
            start_time = time.time()
            if test_type == 'preview':
                original_content = original_generator.generate_quick_preview(test_session_data)
            else:
                original_content = original_generator.generate_complete_etp(test_session_data)
            original_time = time.time() - start_time
            
            results['original'] = {
                'time': round(original_time, 2),
                'content_size': len(original_content),
                'success': True
            }
        except Exception as e:
            results['original'] = {
                'time': 0,
                'content_size': 0,
                'success': False,
                'error': str(e)
            }
        
        # Teste com gerador otimizado
        try:
            optimized_generator = OptimizedEtpGenerator(os.getenv('OPENAI_API_KEY'))
            
            start_time = time.time()
            if test_type == 'preview':
                optimized_content = optimized_generator.generate_ultra_fast_preview(test_session_data)
            else:
                optimized_content = optimized_generator.generate_complete_etp_optimized(test_session_data)
            optimized_time = time.time() - start_time
            
            results['optimized'] = {
                'time': round(optimized_time, 2),
                'content_size': len(optimized_content),
                'success': True
            }
        except Exception as e:
            results['optimized'] = {
                'time': 0,
                'content_size': 0,
                'success': False,
                'error': str(e)
            }
        
        # Calcular melhoria
        improvement_percent = 0
        if results['original']['success'] and results['optimized']['success']:
            if results['original']['time'] > 0:
                improvement_percent = round(
                    ((results['original']['time'] - results['optimized']['time']) / results['original']['time']) * 100, 1
                )
        
        return jsonify({
            'success': True,
            'test_type': test_type,
            'results': results,
            'improvement_percent': improvement_percent,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro no teste de performance: {str(e)}'
        }), 500

@etp_optimized_bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar saúde do serviço otimizado"""
    try:
        # Verificar se API key está configurada
        api_key = os.getenv('OPENAI_API_KEY')
        api_configured = bool(api_key)
        
        # Verificar se geradores podem ser instanciados
        generators_available = {
            'original': False,
            'optimized': False
        }
        
        try:
            AdvancedEtpGenerator(api_key or "test")
            generators_available['original'] = True
        except:
            pass
        
        try:
            OptimizedEtpGenerator(api_key or "test")
            generators_available['optimized'] = True
        except:
            pass
        
        return jsonify({
            'status': 'healthy',
            'api_configured': api_configured,
            'generators_available': generators_available,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

