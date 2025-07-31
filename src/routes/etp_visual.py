from flask import Blueprint, request, jsonify, session, send_file, make_response
import time
import json
import os
from datetime import datetime
from ..utils.etp_generator_ultra_fast import UltraFastEtpGenerator
from ..utils.etp_visual_formatter import EtpVisualFormatter
import tempfile

etp_visual_bp = Blueprint('etp_visual', __name__)

def get_ultra_fast_generator():
    """Retorna gerador ultra-rápido"""
    api_key = os.getenv('OPENAI_API_KEY')
    return UltraFastEtpGenerator(api_key)

@etp_visual_bp.route('/generate-visual-etp', methods=['POST'])
def generate_visual_etp():
    """Gera ETP com formatação visual profissional baseada no modelo da concorrência"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        method = data.get('method', 'lightning')  # 'lightning' ou 'parallel'
        
        if not session_id:
            return jsonify({'error': 'Session ID é obrigatório'}), 400
        
        # Recuperar dados da sessão
        session_data = session.get(f'etp_data_{session_id}', {})
        
        if not session_data.get('answers'):
            return jsonify({'error': 'Dados da sessão não encontrados'}), 404
        
        # Medir tempo total
        start_time = time.time()
        
        # Gerar conteúdo ETP
        generator = get_ultra_fast_generator()
        
        if method == 'parallel':
            etp_content = generator.generate_parallel_etp(session_data)
        else:
            etp_content = generator.generate_lightning_fast_etp(session_data)
        
        content_generation_time = time.time() - start_time
        
        # Aplicar formatação visual
        format_start = time.time()
        formatter = EtpVisualFormatter()
        formatted_html = formatter.format_etp_with_borders(etp_content, session_data)
        formatting_time = time.time() - format_start
        
        total_time = time.time() - start_time
        
        # Salvar arquivo formatado
        filename = f'etp_visual_{session_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
        filepath = formatter.save_formatted_etp(formatted_html, filename)
        
        # Validação rápida
        validation = generator.validate_etp_speed(etp_content)
        
        return jsonify({
            'success': True,
            'etp_content': etp_content,
            'formatted_html': formatted_html,
            'file_path': filepath,
            'metadata': {
                'method_used': method,
                'content_generation_time': round(content_generation_time, 2),
                'formatting_time': round(formatting_time, 2),
                'total_time': round(total_time, 2),
                'content_size': len(etp_content),
                'html_size': len(formatted_html),
                'sections_found': validation['sections_found'],
                'is_complete': validation['is_complete'],
                'has_visual_formatting': True,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro na geração visual do ETP: {str(e)}'
        }), 500

@etp_visual_bp.route('/download-visual-etp/<session_id>', methods=['GET'])
def download_visual_etp(session_id):
    """Download do ETP formatado em HTML"""
    try:
        # Buscar arquivo mais recente para a sessão
        files = [f for f in os.listdir('/home/ubuntu/etp_ultra_otimizado') 
                if f.startswith(f'etp_visual_{session_id}') and f.endswith('.html')]
        
        if not files:
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
        # Pegar o arquivo mais recente
        latest_file = sorted(files)[-1]
        filepath = os.path.join('/home/ubuntu/etp_ultra_otimizado', latest_file)
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=f'ETP_Formatado_{session_id}.html',
            mimetype='text/html'
        )
        
    except Exception as e:
        return jsonify({'error': f'Erro no download: {str(e)}'}), 500

@etp_visual_bp.route('/preview-visual-etp/<session_id>', methods=['GET'])
def preview_visual_etp(session_id):
    """Preview do ETP formatado no navegador"""
    try:
        # Buscar arquivo mais recente para a sessão
        files = [f for f in os.listdir('/home/ubuntu/etp_ultra_otimizado') 
                if f.startswith(f'etp_visual_{session_id}') and f.endswith('.html')]
        
        if not files:
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
        # Pegar o arquivo mais recente
        latest_file = sorted(files)[-1]
        filepath = os.path.join('/home/ubuntu/etp_ultra_otimizado', latest_file)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        response = make_response(html_content)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        return response
        
    except Exception as e:
        return jsonify({'error': f'Erro no preview: {str(e)}'}), 500

@etp_visual_bp.route('/convert-to-pdf', methods=['POST'])
def convert_to_pdf():
    """Converte ETP formatado para PDF"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'error': 'Session ID é obrigatório'}), 400
        
        # Buscar arquivo HTML mais recente
        files = [f for f in os.listdir('/home/ubuntu/etp_ultra_otimizado') 
                if f.startswith(f'etp_visual_{session_id}') and f.endswith('.html')]
        
        if not files:
            return jsonify({'error': 'Arquivo HTML não encontrado'}), 404
        
        latest_file = sorted(files)[-1]
        html_filepath = os.path.join('/home/ubuntu/etp_ultra_otimizado', latest_file)
        
        # Preparar HTML para PDF
        formatter = EtpVisualFormatter()
        with open(html_filepath, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        pdf_ready_html = formatter.convert_to_pdf_ready(html_content)
        
        # Salvar versão PDF-ready
        pdf_html_path = html_filepath.replace('.html', '_pdf_ready.html')
        with open(pdf_html_path, 'w', encoding='utf-8') as f:
            f.write(pdf_ready_html)
        
        # Converter para PDF usando weasyprint ou similar
        pdf_filename = f'etp_visual_{session_id}.pdf'
        pdf_filepath = os.path.join('/home/ubuntu/etp_ultra_otimizado', pdf_filename)
        
        try:
            import weasyprint
            weasyprint.HTML(filename=pdf_html_path).write_pdf(pdf_filepath)
            conversion_success = True
        except ImportError:
            # Fallback: usar comando do sistema se weasyprint não estiver disponível
            import subprocess
            try:
                subprocess.run([
                    'wkhtmltopdf', 
                    '--page-size', 'A4',
                    '--margin-top', '20mm',
                    '--margin-bottom', '20mm',
                    '--margin-left', '20mm',
                    '--margin-right', '20mm',
                    pdf_html_path, 
                    pdf_filepath
                ], check=True)
                conversion_success = True
            except (subprocess.CalledProcessError, FileNotFoundError):
                conversion_success = False
        
        if conversion_success and os.path.exists(pdf_filepath):
            return jsonify({
                'success': True,
                'pdf_path': pdf_filepath,
                'download_url': f'/api/etp-visual/download-pdf/{session_id}',
                'message': 'PDF gerado com sucesso'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Conversão para PDF não disponível. Use o HTML formatado.',
                'html_path': pdf_html_path
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro na conversão para PDF: {str(e)}'
        }), 500

@etp_visual_bp.route('/download-pdf/<session_id>', methods=['GET'])
def download_pdf(session_id):
    """Download do ETP em formato PDF"""
    try:
        pdf_filename = f'etp_visual_{session_id}.pdf'
        pdf_filepath = os.path.join('/home/ubuntu/etp_ultra_otimizado', pdf_filename)
        
        if not os.path.exists(pdf_filepath):
            return jsonify({'error': 'Arquivo PDF não encontrado'}), 404
        
        return send_file(
            pdf_filepath,
            as_attachment=True,
            download_name=f'ETP_Formatado_{session_id}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': f'Erro no download do PDF: {str(e)}'}), 500

@etp_visual_bp.route('/performance-comparison', methods=['POST'])
def performance_comparison():
    """Compara performance entre métodos de geração"""
    try:
        data = request.get_json()
        
        # Dados de teste
        test_session_data = {
            'answers': {
                '1': 'Sistema integrado de gestão de contratos públicos com IA',
                '2': 'Sim, previsto no PCA 2024 item 15.7',
                '3': 'Lei 14.133/2021, LGPD, Decreto 10.024/2019',
                '4': 'R$ 250.000,00 para licenças anuais e R$ 100.000,00 para implantação',
                '5': 'Não haverá parcelamento da contratação'
            },
            'session_id': 'performance_test'
        }
        
        results = {}
        generator = get_ultra_fast_generator()
        formatter = EtpVisualFormatter()
        
        # Teste Lightning Fast
        try:
            start_time = time.time()
            lightning_content = generator.generate_lightning_fast_etp(test_session_data)
            lightning_generation = time.time() - start_time
            
            format_start = time.time()
            lightning_html = formatter.format_etp_with_borders(lightning_content, test_session_data)
            lightning_formatting = time.time() - format_start
            
            lightning_total = lightning_generation + lightning_formatting
            lightning_validation = generator.validate_etp_speed(lightning_content)
            
            results['lightning'] = {
                'generation_time': round(lightning_generation, 2),
                'formatting_time': round(lightning_formatting, 2),
                'total_time': round(lightning_total, 2),
                'content_size': len(lightning_content),
                'html_size': len(lightning_html),
                'sections_found': lightning_validation['sections_found'],
                'is_complete': lightning_validation['is_complete'],
                'success': True
            }
        except Exception as e:
            results['lightning'] = {
                'success': False,
                'error': str(e)
            }
        
        # Teste Processamento Paralelo
        try:
            start_time = time.time()
            parallel_content = generator.generate_parallel_etp(test_session_data)
            parallel_generation = time.time() - start_time
            
            format_start = time.time()
            parallel_html = formatter.format_etp_with_borders(parallel_content, test_session_data)
            parallel_formatting = time.time() - format_start
            
            parallel_total = parallel_generation + parallel_formatting
            parallel_validation = generator.validate_etp_speed(parallel_content)
            
            results['parallel'] = {
                'generation_time': round(parallel_generation, 2),
                'formatting_time': round(parallel_formatting, 2),
                'total_time': round(parallel_total, 2),
                'content_size': len(parallel_content),
                'html_size': len(parallel_html),
                'sections_found': parallel_validation['sections_found'],
                'is_complete': parallel_validation['is_complete'],
                'success': True
            }
        except Exception as e:
            results['parallel'] = {
                'success': False,
                'error': str(e)
            }
        
        # Calcular melhorias
        baseline_time = 240  # 4 minutos originais
        improvements = {}
        
        for method, result in results.items():
            if result.get('success'):
                total_time = result['total_time']
                improvement = ((baseline_time - total_time) / baseline_time) * 100
                improvements[method] = round(improvement, 1)
        
        return jsonify({
            'success': True,
            'results': results,
            'improvements': improvements,
            'baseline_time': baseline_time,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro no teste de performance: {str(e)}'
        }), 500

