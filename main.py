import sys
import os
from constantes import *
from auxiliares import *

# Criação do Índice
# ==============================================================================================

def criaIndice():
    
    try:

        # Abre o arquivo games.dat para leitura
        with open(ARQ_GAMES, 'rb') as arqGames:

            arqBtree, rrnRaiz = criaArvore()
            # Percorrer o arquivo pegando o número de registros
            numRegistros = struct.unpack('i', arqGames.read(TAM_CAB))[0] 

            # Leia um registro do games.dat
            reg, tam = leiaReg(arqGames)
            chave = reg.split('|')[0]  # Pega a chave do registro
            chave = int(chave)
            offset = 4

            # Contador para os registros lidos
            cont = 0
                
            # Enquanto houver registros a serem lidos no games.dat
            while cont < numRegistros:
                    
                # Insira a chave e o offset no arquivo btree.dat (árvore-b)
                # rrnRaiz = novoRRN(arqBtree) # Cria um novo RRN para a raiz
                chavePro, offsetPro, filhoDpro, promo = insereNaArvore(chave, offset, rrnRaiz, arqBtree)  # Insere na árvore B

                # se teve promoção, crie uma nova raiz
                if promo:
                    
                    novaP = Pagina()
                    novaP.chaves[0] = chavePro
                    novaP.offsets[0] = offsetPro
                    novaP.filhos[0] = rrnRaiz
                    novaP.filhos[1] = filhoDpro
                    novaP.numChaves = 1

                    rrnRaiz = novoRRN(arqBtree)
                    escrevePagina(rrnRaiz, novaP, arqBtree)

                cont += 1  # Incrementa o contador

                # Leia o próximo registro
                offset += tam + 2
                reg, tam = leiaReg(arqGames)

                if not(reg == '' and tam == 0):
                    chave = reg.split('|')[0]  # Pega a chave do registro
                    chave = int(chave)
                        
            print("Índice criado com sucesso.")
            fechaArvore(rrnRaiz, arqBtree)

    except OSError as e:
        print(f"Erro ao criar o índice: {e}")

# ==============================================================================================

# Execução de Operações
# ==============================================================================================

# Função de Busca de um jogo
def buscaJogo(chave):

    try:

        with open(ARQ_BTREE, 'rb') as arqBtree:

            print(f'Busca pelo registro de chave "{chave}"')

            rrn = struct.unpack('i', arqBtree.read(TAM_CAB))[0]

            achou, rrn, pos = buscaNaArvore(int(chave), rrn, arqBtree)

            with open(ARQ_GAMES, 'rb') as arqGames:

                if achou:

                        pag = lePagina(rrn, arqBtree)
                        offset = pag.offsets[pos]
                        arqGames.seek(offset)
                        reg, tam = leiaReg(arqGames)
                        print(f"{reg} ({tam} bytes - offset {offset})")

                else:

                    print("Erro: registro não encontrado!")

            print()
            # Busca a chave na árvore B (btree.dat)
            # Recupera o offset do registro no btree.dat, abra o arquivo games.dat e acesse o offset diretamente.

    except OSError as e:

        print(f"Erro ao abrir '{ARQ_BTREE}': {e}")

# Função de Inserção de um jogo
def insereJogo(registro):

    try:

        chave = int(registro.split('|')[0])  # Extrai a chave do registro

        print(f'Inserção do registro de chave "{chave}"')

        # Abrir o arquivo btree.dat para verificar se a chave já existe no índice
        with open(ARQ_BTREE, 'rb') as arqBtree:

            rrnRaiz = struct.unpack('i', arqBtree.read(TAM_CAB))[0]  # Lê o RRN da raiz
            achou, _, _ = buscaNaArvore(chave, rrnRaiz, arqBtree)  # Verifica se a chave já existe

            if achou:

                print(f"Erro: chave {chave} já existente")
                return

        # Se a chave não existe, continue com a inserção
        with open(ARQ_GAMES, 'ab') as arqGames:  # Abre o arquivo para adicionar no final (modo 'ab')

            offset = arqGames.tell()  # Pega o offset atual, que será o início do novo registro

            tam = len(registro)  # Calcula o tamanho do registro
            arqGames.write(struct.pack('h', tam))  # Escreve o tamanho do registro usando struct
            arqGames.write(registro.encode('utf-8'))  # Escreve o registro

        # Agora insere a chave e o offset no índice (btree.dat)
        with open(ARQ_BTREE, 'r+b') as arqBtree:

            chavePro, offsetPro, filhoDpro, promo = insereNaArvore(chave, offset, rrnRaiz, arqBtree)

            # Se houver promoção, criar uma nova raiz
            if promo:

                pNova = Pagina()
                pNova.chaves[0] = chavePro
                pNova.offsets[0] = offsetPro
                pNova.filhos[0] = rrnRaiz
                pNova.filhos[1] = filhoDpro
                pNova.numChaves = 1

                rrnRaiz = novoRRN(arqBtree)
                escrevePagina(rrnRaiz, pNova, arqBtree)

        print(f"{registro} ({tam} bytes - offset {offset})")
        print()

    except OSError as e:

        print(f"Erro ao inserir o registro: {e}")

# ==============================================================================================

# Impressão das informações da árvore-B
# ==============================================================================================

def imprimeArvore():

    print()

    try:

        with open(ARQ_BTREE, 'rb') as arqBtree:

            rrnRaiz = struct.unpack('i', arqBtree.read(TAM_CAB))[0]  # Lê o RRN da raiz
            numPaginas = (os.path.getsize(ARQ_BTREE) - TAM_CAB) // TAM_PAG  # Calcula o número de páginas

            # Itera por todas as páginas da árvore
            for rrn in range(numPaginas):

                if rrn == rrnRaiz:
                    print("- - - - - - Raiz - - - - - -")

                pagina = lePagina(rrn, arqBtree)  # Lê a página com o RRN atual

                print(f"Página {rrn}:")
                
                # Exibe as chaves, completando até ordem - 1 com -1
                print("Chaves =", end=" ")
                for i in range(ORDEM - 1):  # ORDEM - 1 é o máximo de chaves possíveis
                    if i < len(pagina.chaves) and pagina.chaves[i] != -1:
                        print(pagina.chaves[i], end=" | ")
                    else:
                        print(-1, end=" | ")
                print()

                # Exibe os offsets, completando até ordem - 1 com -1
                print("Offsets =", end=" ")
                for i in range(ORDEM - 1):  # ORDEM - 1 é o máximo de offsets possíveis
                    if i < len(pagina.offsets) and pagina.offsets[i] != -1:
                        print(pagina.offsets[i], end=" | ")
                    else:
                        print(-1, end=" | ")
                print()

                # Exibe as filhas (não precisa completar, pois sempre são ORDEM)
                print("Filhas =", end=" ")
                for filho in pagina.filhos:
                    print(filho, end=" | ")
                print()

                if rrn == rrnRaiz:
                    print("- - - - - - - - - - - - - - -")

                print()

        print('O índice "btree.dat" foi impresso com sucesso!')
        print()

    except OSError as e:

        print(f"Erro ao abrir '{ARQ_BTREE}': {e}")
    
def execucao(nomeArq):

    try:

        with open(nomeArq, "r") as arq:

            linhas = arq.readlines()  # Transforma as linhas em um array
            tamLinha = len(linhas)  # Pega o número de linhas a partir do tamanho do array
            i = 0  # Inicializa o contador

            while i < tamLinha:  # Enquanto o contador for menor que o número de linhas

                linha = linhas[i].strip()  # Remove espaços em branco e quebras de linha no início e no fim

                if linha:  # Verifica se a linha não está vazia
                    
                    operacao = linha[0]  # Pega o primeiro caractere da linha para determinar a operação

                    if len(linha.split()) > 1:  # Verifica se a linha tem partes suficientes para extrair a chave

                        chave = linha.split()[1]  # Pega a chave, que é o segundo elemento após o split
                        chave = chave.split(sep='|')[0] # Pega a chave que está antes do Pipe

                        if operacao == "b":  # Se o char for igual a b, é busca

                            buscaJogo(chave)

                        elif operacao == "i":  # Se o char for igual a i, seria inserção

                            indiceEspaco = linha.index(' ')
                            registro = linha[indiceEspaco + 1:] # Fatiar a string a partir do índice do primeiro espaço

                            insereJogo(registro)

                        else:

                            print(f"Operação '{operacao}' não reconhecida.")

                    else:

                        print("Linha mal formatada ou faltando chave: ", linha)

                i += 1  # Incrementa o contador para processar a próxima linha

    except OSError as e:

        print(f"Erro ao abrir '{nomeArq}': {e}")

if __name__ == "__main__":

    if len(sys.argv) < 2:

        print("Uso: python main.py -c")
        print("Uso: python main.py -e <arquivo de operações>")
        print("Uso: python main.py -p")
        sys.exit(1)

    if sys.argv[1] == "-c":

        criaIndice()

    elif len(sys.argv) == 3 and sys.argv[1] == '-e':

        nomeArq = sys.argv[2]
        execucao(nomeArq)
        print('As operações do arquivo "arquivo_operacoes.txt" foram executadas com sucesso!')

    elif sys.argv[1] == "-p":
 
        imprimeArvore()

    else:

        print("Opção inválida")
        sys.exit(1)