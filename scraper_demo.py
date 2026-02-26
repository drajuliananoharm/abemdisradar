import requests
from bs4 import BeautifulSoup
import json
import time

def scrape_fundo_brasil():
    """Raspagem real dos editais do Fundo Brasil de Direitos Humanos."""
    url = "https://www.fundobrasil.org.br/nosso-trabalho/apoio-a-sociedade-civil/editais-gerais-e-especificos/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    editais = []
    
    print(f"Buscando no Fundo Brasil: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Filtra apenas links que contêm '/edital/'
        cards = [a for a in soup.select('a.group.flex') if '/edital/' in a.get('href', '')]
        
        for i, card in enumerate(cards):
            try:
                # Título
                title_elem = card.select_one('div.text-xl, div.lg\\:text-2xl.font-bold')
                title = title_elem.get_text(strip=True) if title_elem else "Edital Fundo Brasil"
                
                # Link
                link = card.get('href', '#')
                if not link.startswith('http'):
                    link = "https://www.fundobrasil.org.br" + (link if link.startswith('/') else '/' + link)
                
                # Prazo
                deadline = "Ver site"
                deadline_container = card.select_one('div.mt-auto')
                if deadline_container:
                    deadline_text = deadline_container.get_text(strip=True)
                    if "PRAZO" in deadline_text.upper():
                        deadline = deadline_text.split(":")[-1].strip()
                
                # Status
                status_elem = card.select_one('div.text-sm.font-bold')
                status = status_elem.get_text(strip=True) if status_elem else "Aberto"

                # Só ignora se for explicitamente encerrado
                if "Encerrado" in status or "Fechado" in status.capitalize():
                    continue 

                editais.append({
                    "id": f"fb-{i}",
                    "title": title,
                    "org": "Fundo Brasil",
                    "category": "direitos",
                    "deadline": deadline,
                    "amount": "A consultar",
                    "saved": False,
                    "desc": f"Edital Fundo Brasil. Status: {status}",
                    "link": link
                })
            except Exception as e:
                print(f"Erro ao processar card do Fundo Brasil: {e}")
                
    except Exception as e:
        print(f"Erro ao acessar Fundo Brasil: {e}")
        
    return editais

def scrape_gife():
    """Raspagem real dos editais do GIFE."""
    url = "https://gife.org.br/editais/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    editais = []
    
    print(f"Buscando no GIFE: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Encontra todos os h1 (que são os títulos dos posts de editais identificados na GIFE)
        titles = soup.select('h1')
        
        for i, title_elem in enumerate(titles):
            try:
                title = title_elem.get_text(strip=True)
                # Filtra apenas títulos que pareçam ser de editais ou listas
                if not title or len(title) < 15 or "Apoio" in title: continue
                if "Editais" == title: continue
                
                # O link geralmente está dentro do h1 ou no próximo 'a'
                link_elem = title_elem.select_one('a') or title_elem.find_next('a', class_='text-uppercase')
                link = link_elem.get('href', '#') if link_elem else "#"

                # Descrição: pega o próximo parágrafo
                desc_elem = title_elem.find_next('p')
                desc = desc_elem.get_text(strip=True) if desc_elem else "Confira os detalhes no site do GIFE."
                
                deadline = "Ver no site"
                if "até" in desc.lower():
                    parts = desc.lower().split("até")
                    if len(parts) > 1:
                        deadline_candidate = parts[1].strip()[:30].strip()
                        if "." in deadline_candidate: deadline_candidate = deadline_candidate.split(".")[0]
                        deadline = deadline_candidate

                editais.append({
                    "id": f"gife-{i}",
                    "title": title,
                    "org": "GIFE",
                    "category": "saude",
                    "deadline": deadline,
                    "amount": "Variável",
                    "saved": False,
                    "desc": desc[:150] + ("..." if len(desc) > 150 else ""),
                    "link": link
                })
            except Exception as e:
                print(f"Erro ao processar post do GIFE: {e}")
                
    except Exception as e:
        print(f"Erro ao acessar GIFE: {e}")
        
    return editais


def save_to_json(data, filename="editais_raspados.json"):
    """Salva os dados extraídos em um arquivo JSON que poderia ser consumido pelo Dashboard JS."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Dados salvos com sucesso em {filename}")


if __name__ == "__main__":
    print("--- Rastreador de Editais ABEMDIS (Módulo Real) ---")
    
    # Carrega lista de IDs para ignorar (blacklist.json)
    blacklist = []
    try:
        with open("blacklist.json", "r", encoding="utf-8") as f:
            blacklist = json.load(f)
            print(f"Blacklist carregada: {len(blacklist)} itens ignorados.")
    except FileNotFoundError:
        print("Nenhuma blacklist encontrada. Continuando normalmente.")
    except Exception as e:
        print(f"Erro ao carregar blacklist: {e}")

    todas_oportunidades = []
    
    # Executa cada scraper
    dados_fb = scrape_fundo_brasil()
    todas_oportunidades.extend(dados_fb)
    
    dados_gife = scrape_gife()
    todas_oportunidades.extend(dados_gife)
    
    # Filtra itens na blacklist
    if blacklist:
        original_count = len(todas_oportunidades)
        todas_oportunidades = [o for o in todas_oportunidades if o['id'] not in blacklist]
        diff = original_count - len(todas_oportunidades)
        if diff > 0:
            print(f"Filtrados {diff} editais da blacklist.")

    print(f"\nTotal Geral: {len(todas_oportunidades)} editais encontrados.")
    
    if todas_oportunidades:
        save_to_json(todas_oportunidades)
        print("Dados reais salvos com sucesso.")
    else:
        print("Nenhuma oportunidade encontrada. Verifique os seletores CSS.")

