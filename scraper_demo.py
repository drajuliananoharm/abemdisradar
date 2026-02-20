import requests
from bs4 import BeautifulSoup
import json
import time

def scrape_fundo_brasil_demo():
    """
    Função demonstrativa de como raspar informações de editais 
    do Fundo Brasil de Direitos Humanos ou portais similares.
    
    Atenção: Na prática, você precisa ajustar os seletores CSS 
    baseando-se no HTML real da página no momento da execução.
    """
    
    print("Iniciando raspagem de demonstração...")
    
    # URL fictícia/exemplificativa para a busca de editais
    url = "https://fundobrasil.org.br/editais-abertos/"
    
    # Adicionando um User-Agent para evitar bloqueios simples
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    editais = []
    
    try:
        # Nota: Estamos fazendo a requisição para fins didáticos.
        # Em um cenário real, você analisaria o Response.
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Simulando uma busca por elementos de 'card' de edital
        # IMPORTANTE: Estes seletores são imaginários e precisam ser 
        # adaptados para a estrutura HTML real da página em questão.
        
        cards = soup.select('.edital-card') # Exemplo de seletor
        
        if not cards:
            print("Nenhum card de edital encontrado usando os seletores atuais.")
            print("Neste demo, vamos gerar dados fictícios como se tivessem sido raspados com sucesso.")
            
            # Gerando dados de demonstração
            editais = [
                {
                    "id": 101,
                    "title": "[DEMO RASPAGEM AUTOMÁTICA] Edital de Direitos Humanos 2026",
                    "org": "Fundo Brasil",
                    "category": "direitos",
                    "deadline": "15 Abr 2026",
                    "amount": "R$ 80.000",
                    "saved": False,
                    "desc": "Dados atualizados hoje automaticamente via GitHub Actions.",
                    "link": url
                },
                {
                    "id": 102,
                    "title": "[DEMO RASPAGEM AUTOMÁTICA] Apoio a Saúde e Associações",
                    "org": "Fundação X",
                    "category": "saude",
                    "deadline": "30 Mai 2026",
                    "amount": "R$ 150.000",
                    "saved": False,
                    "desc": "Edital recém-publicado identificado pelo robô rastreador.",
                    "link": url
                }
            ]
        else:
            for i, card in enumerate(cards):
                titulo = card.select_one('.titulo-edital')
                data_limite = card.select_one('.prazo-inscricao')
                link = card.select_one('a')
                
                editais.append({
                    "id": 200 + i,
                    "title": titulo.text.strip() if titulo else "Sem Título",
                    "org": "Fundo Brasil",
                    "category": "pesquisa", # Placeholder genérico
                    "deadline": data_limite.text.strip() if data_limite else "Não informado",
                    "amount": "A definir",
                    "saved": False,
                    "desc": "Edital capturado via automação",
                    "link": link['href'] if link and 'href' in link.attrs else ""
                })
                
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar {url}: {e}")
        print("Fallback: Utilizando dados de demonstração salvos.")
        
        editais = [
            {
                "id": 999,
                "title": "Edital Demonstração Offline (Erro Rede)",
                "org": "Sistema Interno",
                "category": "saude",
                "deadline": "N/A",
                "amount": "R$ 0",
                "saved": False,
                "desc": "Edital falhou no carregamento da rede",
                "link": "#"
            }
        ]

    return editais


def save_to_json(data, filename="editais_raspados.json"):
    """Salva os dados extraídos em um arquivo JSON que poderia ser consumido pelo Dashboard JS."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Dados salvos com sucesso em {filename}")


if __name__ == "__main__":
    print("--- Rastreador de Editais ABEMDIS (Módulo Scraper) ---")
    print("Simulando coleta de editais do Fundo Brasil...")
    time.sleep(1) # Simulando tempo de rede
    
    dados_extraidos = scrape_fundo_brasil_demo()
    
    print(f"\nForam encontrados {len(dados_extraidos)} editais.")
    for edital in dados_extraidos:
        print(f"- {edital['titulo']} (Prazo: {edital['prazo']})")
        
    save_to_json(dados_extraidos)
    print("Processo concluído.")
