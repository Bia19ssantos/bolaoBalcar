def carregar_jogos():
    """Carrega os jogos do Brasil e normaliza as datas vindas do Google Sheets."""
    try:
        df = pd.read_csv(URL_JOGOS)
        df.columns = df.columns.str.strip()
        
        jogos_dict = {}
        fuso_br = pytz.timezone('America/Sao_Paulo')
        
        for _, row in df.iterrows():
            id_jogo = str(row['Id']).strip()
            data_texto = str(row['Data']).strip()
            encerrado_val = str(row['Encerrado']).strip().upper()
            is_encerrado = True if encerrado_val in ['TRUE', '1', '1.0'] else False
            
            # Formatos compatíveis com a planilha real (Ano-Mês-Dia)
            formatos_data = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M",
                "%d/%m/%Y %H:%M"
            ]
            
            dt_aware = None
            for formato in formatos_data:
                try:
                    # Tenta ler no padrão direto
                    dt_naive = datetime.datetime.strptime(data_texto, formato)
                    dt_aware = fuso_br.localize(dt_naive)
                    break
                except:
                    try:
                        # Tratamento caso os minutos tenham vindo sem o zero (ex: '12:0' -> '12:00')
                        if ":" in data_texto and len(data_texto.split(":")[-1]) == 1:
                            data_corrigida = data_texto + "0"
                            dt_naive = datetime.datetime.strptime(data_corrigida, formato)
                            dt_aware = fuso_br.localize(dt_naive)
                            break
                    except:
                        continue
            
            # Se nenhum formato casar, usa a hora atual como fallback de segurança
            if dt_aware is None:
                dt_aware = datetime.datetime.now(fuso_br)
            
            jogos_dict[id_jogo] = {
                "confronto": str(row['Confronto']).strip(),
                "data_completa": dt_aware,
                "resultado": str(row['Resultado']).strip() if pd.notna(row['Resultado']) else None,
                "encerrado": is_encerrado
            }
        return jogos_dict
    except Exception as e:
        st.error(f"Erro ao ler aba 'jogos': {e}")
        return {}
