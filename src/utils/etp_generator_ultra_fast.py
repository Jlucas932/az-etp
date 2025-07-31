import os
import json
from typing import Dict, List, Optional
import openai
from datetime import datetime
import asyncio
import concurrent.futures
import time

class UltraFastEtpGenerator:
    """Gerador ultra-otimizado de ETP - Meta: 2 minutos ou menos"""
    
    def __init__(self, openai_api_key: str):
        self.client = openai.OpenAI(api_key=openai_api_key)
        
        # Estrutura otimizada com prompts mais concisos
        self.etp_sections = {
            "1": "INTRODUÇÃO",
            "2": "OBJETO DO ESTUDO E ESPECIFICAÇÕES GERAIS", 
            "3": "DESCRIÇÃO DOS REQUISITOS DA CONTRATAÇÃO",
            "4": "ESTIMATIVA DAS QUANTIDADES E VALORES",
            "5": "LEVANTAMENTO DE MERCADO E JUSTIFICATIVA DA ESCOLHA DA SOLUÇÃO",
            "6": "ESTIMATIVA DO VALOR DA CONTRATAÇÃO",
            "7": "DESCRIÇÃO DA SOLUÇÃO COMO UM TODO",
            "8": "JUSTIFICATIVA PARA O PARCELAMENTO OU NÃO DA CONTRATAÇÃO",
            "9": "DEMONSTRATIVO DOS RESULTADOS PRETENDIDOS",
            "10": "PROVIDÊNCIAS ADOTADAS ANTERIORMENTE PELA ADMINISTRAÇÃO",
            "11": "CONTRATAÇÕES CORRELATAS OU INTERDEPENDENTES",
            "12": "AVALIAÇÃO DOS IMPACTOS AMBIENTAIS",
            "13": "ANÁLISE DE RISCOS",
            "14": "CONCLUSÃO E POSICIONAMENTO FINAL"
        }

    def generate_lightning_fast_etp(self, session_data: Dict, context_data: Dict = None) -> str:
        """Gera ETP em velocidade máxima - otimizado para 2 minutos"""
        try:
            start_time = time.time()
            answers = session_data.get('answers', {})
            
            # Prompt ultra-conciso e otimizado
            prompt = self._build_lightning_prompt(answers)
            
            # Usar modelo mais rápido disponível
            response = self.client.chat.completions.create(
                model="gpt-4.1-nano",  # Modelo mais rápido
                messages=[
                    {
                        "role": "system",
                        "content": "Especialista em ETP. Gere conteúdo técnico completo, conciso e conforme Lei 14.133/21. Seja direto e eficiente."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=5000,  # Reduzido para velocidade
                temperature=0.1,   # Mais determinístico = mais rápido
                top_p=0.9         # Otimização adicional
            )
            
            content = response.choices[0].message.content.strip()
            generation_time = time.time() - start_time
            
            # Validação rápida
            sections_found = sum(1 for i in range(1, 15) if f"{i}." in content)
            
            # Se incompleto, usar fallback ultra-rápido
            if sections_found < 12:
                print(f"⚠️ ETP incompleto ({sections_found}/14), usando fallback rápido")
                content = self._generate_ultra_fast_fallback(answers)
            
            # Formatação final otimizada
            final_content = self._format_lightning_etp(content, answers)
            
            print(f"⚡ ETP gerado em {generation_time:.2f}s com {sections_found}/14 seções")
            return final_content
            
        except Exception as e:
            print(f"Erro na geração ultra-rápida: {e}")
            return self._generate_ultra_fast_fallback(session_data.get('answers', {}))

    def generate_parallel_etp(self, session_data: Dict, context_data: Dict = None) -> str:
        """Gera ETP usando processamento paralelo para máxima velocidade"""
        try:
            start_time = time.time()
            answers = session_data.get('answers', {})
            
            # Dividir em 2 grupos para processamento paralelo
            group1_sections = list(range(1, 8))   # Seções 1-7
            group2_sections = list(range(8, 15))  # Seções 8-14
            
            # Prompts otimizados para cada grupo
            prompt1 = self._build_group_prompt(answers, group1_sections, "primeira parte")
            prompt2 = self._build_group_prompt(answers, group2_sections, "segunda parte")
            
            # Executar em paralelo
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                future1 = executor.submit(self._generate_section_group, prompt1)
                future2 = executor.submit(self._generate_section_group, prompt2)
                
                # Aguardar resultados
                content1 = future1.result(timeout=60)  # 1 minuto max por grupo
                content2 = future2.result(timeout=60)
            
            # Combinar resultados
            combined_content = f"{content1}\n\n{content2}"
            generation_time = time.time() - start_time
            
            # Formatação final
            final_content = self._format_lightning_etp(combined_content, answers)
            
            print(f"⚡ ETP paralelo gerado em {generation_time:.2f}s")
            return final_content
            
        except Exception as e:
            print(f"Erro na geração paralela: {e}")
            return self._generate_ultra_fast_fallback(session_data.get('answers', {}))

    def _build_lightning_prompt(self, answers: Dict) -> str:
        """Constrói prompt ultra-otimizado para velocidade máxima"""
        return f"""
        Gere ETP COMPLETO com 14 seções obrigatórias Lei 14.133/21. SEJA CONCISO MAS TÉCNICO.

        DADOS: Necessidade: {answers.get('1', 'solução tecnológica')} | PCA: {answers.get('2', 'Sim')} | Normas: {answers.get('3', 'Lei 14.133/21')} | Valores: {answers.get('4', 'pesquisa mercado')} | Parcelamento: {answers.get('5', 'Não')}

        GERE TODAS AS 14 SEÇÕES (6 parágrafos cada):
        1.INTRODUÇÃO 2.OBJETO E ESPECIFICAÇÕES 3.REQUISITOS 4.ESTIMATIVA QUANTIDADES/VALORES+tabela 5.MERCADO/JUSTIFICATIVA 6.VALOR CONTRATAÇÃO 7.SOLUÇÃO COMPLETA 8.PARCELAMENTO 9.RESULTADOS 10.PROVIDÊNCIAS ANTERIORES 11.CONTRATOS CORRELATOS 12.IMPACTOS AMBIENTAIS 13.RISCOS+tabela 14.CONCLUSÃO

        Use linguagem técnica Lei 14.133/21. Inclua tabelas seções 4 e 13.
        """

    def _build_group_prompt(self, answers: Dict, sections: List[int], group_name: str) -> str:
        """Constrói prompt para grupo de seções"""
        section_names = [f"{i}.{self.etp_sections[str(i)]}" for i in sections]
        
        return f"""
        Gere {group_name} do ETP com seções: {' | '.join(section_names)}

        DADOS: {answers.get('1', 'solução')} | {answers.get('2', 'PCA')} | {answers.get('3', 'Lei 14.133/21')} | {answers.get('4', 'valores')} | {answers.get('5', 'parcelamento')}

        Cada seção: 6 parágrafos técnicos. Linguagem formal Lei 14.133/21.
        {f'Inclua tabela na seção 4.' if 4 in sections else ''}
        {f'Inclua tabela riscos na seção 13.' if 13 in sections else ''}
        """

    def _generate_section_group(self, prompt: str) -> str:
        """Gera grupo de seções"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[
                    {"role": "system", "content": "Especialista ETP. Conteúdo técnico conciso Lei 14.133/21."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2500,
                temperature=0.1
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Erro na geração de grupo: {e}")
            return "Erro na geração desta seção."

    def _format_lightning_etp(self, content: str, answers: Dict) -> str:
        """Formatação final otimizada"""
        header = f"""ESTUDO TÉCNICO PRELIMINAR

Data: {datetime.now().strftime('%d/%m/%Y')}
Objeto: {answers.get('1', 'Contratação conforme necessidade identificada')}

"""
        
        footer = f"""

---
Documento elaborado em conformidade com a Lei nº 14.133/2021
Data: {datetime.now().strftime('%d/%m/%Y')}
Gerado em modo ultra-rápido"""
        
        return header + content + footer

    def _generate_ultra_fast_fallback(self, answers: Dict) -> str:
        """Fallback ultra-rápido com estrutura mínima garantida"""
        objeto = answers.get('1', 'solução tecnológica')
        
        sections_content = []
        
        # Gerar seções básicas rapidamente
        basic_sections = {
            "1. INTRODUÇÃO": f"O presente ETP foi elaborado conforme Lei 14.133/2021 para {objeto}. Este documento demonstra viabilidade técnica e econômica. A elaboração observa diretrizes legais vigentes. O planejamento garante eficiência e transparência. A metodologia baseia-se em análise técnica detalhada. O documento atende aos princípios constitucionais.",
            
            "2. OBJETO DO ESTUDO E ESPECIFICAÇÕES GERAIS": f"{answers.get('1', 'Contratação necessária para atender demanda operacional')}. A execução ocorrerá conforme especificações técnicas. O objeto visa atender necessidades identificadas. A previsão no PCA: {answers.get('2', 'Conforme planejamento aprovado')}. A natureza caracteriza-se como contratação comum. A finalidade é melhorar processos administrativos.",
            
            "3. DESCRIÇÃO DOS REQUISITOS DA CONTRATAÇÃO": f"Requisitos técnicos baseados em necessidades operacionais. Requisitos de sustentabilidade conforme normas vigentes. {answers.get('3', 'Lei 14.133/2021 e regulamentação aplicável')}. Requisitos de segurança incluem proteção de dados. Requisitos funcionais abrangem funcionalidades necessárias. Critérios de aceitação definidos objetivamente.",
            
            "4. ESTIMATIVA DAS QUANTIDADES E VALORES": f"{answers.get('4', 'Estimativa baseada em pesquisa de mercado')}. Metodologia considera custos diretos e indiretos. Pesquisa realizada junto a fornecedores qualificados. Valores ajustados conforme índices de mercado.\n\n| Item | Qtd | Unidade | Valor Unit. | Valor Total |\n|------|-----|---------|-------------|-------------|\n| {objeto} | 1 | Un | R$ 100.000 | R$ 100.000 |\n| **TOTAL** | | | | **R$ 100.000** |",
            
            "5. LEVANTAMENTO DE MERCADO E JUSTIFICATIVA DA ESCOLHA DA SOLUÇÃO": "Levantamento identificou soluções disponíveis no mercado. Análise contemplou aspectos técnicos e econômicos. Solução escolhida apresenta melhor custo-benefício. Pesquisa envolveu fornecedores qualificados. Avaliação considerou funcionalidades e desempenho. Justificativa baseia-se em critérios objetivos.",
            
            "6. ESTIMATIVA DO VALOR DA CONTRATAÇÃO": "Valor estimado baseado em pesquisa abrangente. Estimativa observa princípios de economicidade. Considerados custos de implementação e operação. Análise de viabilidade demonstra justificativa. Metodologia considera complexidade técnica. Valores validados com contratos similares.",
            
            "7. DESCRIÇÃO DA SOLUÇÃO COMO UM TODO": "Solução contempla aspectos necessários para atendimento. Integração entre componentes cuidadosamente planejada. Benefícios incluem melhoria de eficiência operacional. Implementação será gradual e controlada. Solução garante modernização dos processos. Resultado esperado é otimização geral.",
            
            "8. JUSTIFICATIVA PARA O PARCELAMENTO OU NÃO DA CONTRATAÇÃO": f"{answers.get('5', 'Contratação será integral, sem parcelamento')}. Análise demonstrou que unificação proporciona economia. Parcelamento resultaria em perda de eficiência. Unidade contratual garante melhor controle. Gestão unificada facilita coordenação. Responsabilização do fornecedor é otimizada.",
            
            "9. DEMONSTRATIVO DOS RESULTADOS PRETENDIDOS": "Resultados incluem melhoria na qualidade dos serviços. Contratação proporcionará maior eficiência operacional. Benefícios quantitativos incluem redução de tempo. Benefícios qualitativos abrangem satisfação dos usuários. Modernização tecnológica dos procedimentos. Fortalecimento da capacidade operacional.",
            
            "10. PROVIDÊNCIAS ADOTADAS ANTERIORMENTE PELA ADMINISTRAÇÃO": "Administração realizou estudos preliminares necessários. Foram consultados especialistas para validação. Análises de experiências similares foram conduzidas. Planejamento orçamentário foi adequadamente realizado. Definição de especificações técnicas foi refinada. Aprovação da alta administração foi obtida.",
            
            "11. CONTRATAÇÕES CORRELATAS OU INTERDEPENDENTES": "Não foram identificadas contratações correlatas impactantes. Análise do portfólio confirmou independência da contratação. Eventuais sinergias serão aproveitadas para otimização. Gestão integrada será implementada quando aplicável. Coordenação evitará sobreposições desnecessárias. Monitoramento contínuo será mantido.",
            
            "12. AVALIAÇÃO DOS IMPACTOS AMBIENTAIS": "Contratação não apresenta impactos ambientais significativos. Critérios de sustentabilidade serão incorporados. Fornecedor deverá demonstrar conformidade ambiental. Medidas de mitigação serão implementadas quando necessário. Conformidade com legislação ambiental é obrigatória. Práticas sustentáveis serão priorizadas.",
            
            "13. ANÁLISE DE RISCOS": "Principais riscos relacionam-se à disponibilidade de fornecedores. Variações de preço representam risco médio.\n\n| Risco | Probabilidade | Impacto | Mitigação |\n|-------|---------------|---------|----------|\n| Fornecedores indisponíveis | Baixa | Médio | Pesquisa ampla |\n| Variação preços | Média | Alto | Cláusulas reajuste |\n| Problemas técnicos | Baixa | Alto | Especificações detalhadas |\n\nMonitoramento contínuo será implementado. Medidas preventivas foram definidas.",
            
            "14. CONCLUSÃO E POSICIONAMENTO FINAL": "Estudos demonstram viabilidade técnica e econômica. Solução atende integralmente às necessidades identificadas. Riscos são gerenciáveis através das medidas propostas. Recomenda-se prosseguimento do processo de contratação. Especificações estabelecidas devem ser observadas. Contratação proporcionará benefícios significativos."
        }
        
        # Montar conteúdo final
        content = "\n\n".join([f"{title}\n\n{content}" for title, content in basic_sections.items()])
        
        return f"""ESTUDO TÉCNICO PRELIMINAR

Data: {datetime.now().strftime('%d/%m/%Y')}

{content}

---
Documento elaborado em conformidade com a Lei nº 14.133/2021
Data: {datetime.now().strftime('%d/%m/%Y')}
Gerado em modo fallback ultra-rápido"""

    def validate_etp_speed(self, etp_content: str) -> Dict:
        """Validação rápida focada em velocidade"""
        sections_found = 0
        for i in range(1, 15):
            if f"{i}." in etp_content:
                sections_found += 1
        
        return {
            'sections_found': sections_found,
            'is_complete': sections_found >= 12,
            'content_size': len(etp_content),
            'has_tables': '|' in etp_content
        }

