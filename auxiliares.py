import os
from constantes import *
from pagina import *

# Funções Auxiliares
# ==============================================================================================

def criaArvore():

    arqBtree = open(ARQ_BTREE, 'wb+')

    # Criar uma árvore vazia 
    rrnRaiz = 0
    p = Pagina()
    # escreve o cabeçalho
    arqBtree.write(struct.pack('i', rrnRaiz))
    # escreve uma página vazia
    escrevePagina(rrnRaiz, p, arqBtree)
    return arqBtree, rrnRaiz

def fechaArvore(rrnRaiz, arq):
    arq.seek(0)
    arq.write(struct.pack('i', rrnRaiz))
    arq.close()


def escrevePagina(rrn, pag, arq):

    offset = rrn * TAM_PAG + TAM_CAB # Calcula o offset da página
    arq.seek(offset) # Posiciona o ponteiro do arquivo no offset
    valores = [pag.numChaves] + pag.chaves + pag.offsets + pag.filhos # Monta a lista de valores

    valoresBytes = struct.pack(FORMATO_PAG, *valores) # Empacota os valores em bytes
    arq.write(valoresBytes) # Escreve os valores no arquivo

def lePagina(rrn, arq):

    offset = rrn * TAM_PAG + TAM_CAB # Calcula o offset da página
    arq.seek(offset) # Posiciona o ponteiro do arquivo no offset
    valoresBytes = arq.read(TAM_PAG) # Lê os bytes da página
    
    valores = struct.unpack(FORMATO_PAG, valoresBytes) # Desempacota os bytes em valores

    pag = Pagina() # Cria um objeto Pagina
    pag.numChaves = valores[0] # Atribui o número de chaves
    pag.chaves = list(valores[1:ORDEM]) # Atribui as chaves
    pag.offsets = list(valores[ORDEM:ORDEM + ORDEM - 1]) # Atribui os offsets
    pag.filhos = list(valores[ORDEM + ORDEM - 1:]) # Atribui os filhos
    
    return pag # Retorna a página

def buscaNaPagina(chave, pag):

    pos = 0 # Inicializa a posição

    while pos < pag.numChaves and chave > pag.chaves[pos]: # Enquanto a posição for menor que o número de chaves e a chave for maior que a chave na posição

        pos += 1 # Incrementa a posição
    
    if pos < pag.numChaves and chave == pag.chaves[pos]: # Se a posição for menor que o número de chaves e a chave for igual a chave na posição

        return True, pos # Encontrou a chave
    
    else:

        return False, pos # Não encontrou a chave

def insereNaPagina(chave, offset, filhoD, pag):

    if pag.numChaves == ORDEM - 1: # Se a pag estiver cheia, aumente sua capacidade

        pag.chaves.append(NULO) # Adiciona um valor nulo na lista de chaves
        pag.offsets.append(NULO) # Adiciona um valor nulo na lista de offsets
        pag.filhos.append(NULO) # Adiciona um valor nulo na lista de filhos

    i = pag.numChaves # Inicializa i com o número de chaves

    while i > 0 and chave < pag.chaves[i - 1]: # Enquanto i for maior que 0 e a chave for menor que a chave na posição i - 1

        pag.chaves[i] = pag.chaves[i - 1] # Atribui a chave na posição i - 1 para a posição i
        pag.offsets[i] = pag.offsets[i - 1] # Atribui o offset na posição i - 1 para a posição i
        pag.filhos[i + 1] = pag.filhos[i] # Atribui o filho na posição i para a posição i + 1
        i -= 1 # Decrementa i
    
    pag.chaves[i] = chave # Atribui a chave na posição i
    pag.offsets[i] = offset # Atribui o offset na posição i
    pag.filhos[i + 1] = filhoD # Atribui o filho na posição i + 1
    pag.numChaves += 1 # Incrementa o número de chaves

def novoRRN(arq):
    
    arq.seek(0, os.SEEK_END) # Posiciona o ponteiro do arquivo no final
    offset = arq.tell() # Pega a posição do ponteiro
    return ((offset - TAM_CAB) // TAM_PAG) # Retorna o RRN

def dividePagina(chave, offset, filhoD, pag, arq):

    insereNaPagina(chave, offset, filhoD, pag) # Insere chave e filhoD na página
    
    meio = ORDEM // 2 # Calcula o meio da página
    chavePro = pag.chaves[meio] # Pega a chave promovida
    offsetPro = pag.offsets[meio] # Pega o offset promovido
    filhoDpro = novoRRN(arq) # Pega o RRN do filho promovido

    # Ajusta pAtual para conter as primeiras chaves e filhos
    pAtual = Pagina() # Cria um objeto Pagina
    pAtual.numChaves = meio # Atribui o número de chaves como o meio

    chaves = pag.chaves[:meio] # Pega as chaves até o meio
    chaves += [NULO] * (ORDEM - 1 - len(chaves)) # Adiciona valores nulos até a ordem - 1
    pAtual.chaves = chaves # Atribui as chaves como as primeiras chaves

    offsets = pag.offsets[:meio] # Pega os offsets até o meio
    offsets += [NULO] * (ORDEM - 1 - len(offsets)) # Adiciona valores nulos até a ordem - 1
    pAtual.offsets = offsets # Atribui os offsets como os primeiros offsets

    filhos = pag.filhos[:meio + 1]
    filhos += [NULO] * (ORDEM - len(filhos)) # Adiciona valores nulos até a ordem
    pAtual.filhos = filhos # Atribui os filhos como os primeiros filhos

    # Cria a nova página (pNova)
    pNova = Pagina() # Cria um objeto Pagina
    pNova.numChaves = ORDEM - meio - 1 # Atribui o número de chaves como a diferença entre a ordem e o meio - 1

    chaves = pag.chaves[meio + 1:] # Pega as chaves a partir do meio + 1
    chaves += [NULO] * (ORDEM - 1 - len(chaves)) # Adiciona valores nulos até a ordem - 1
    pNova.chaves = chaves # Atribui as chaves como as chaves a partir do meio + 1

    offsets = pag.offsets[meio + 1:] # Pega os offsets a partir do meio + 1
    offsets += [NULO] * (ORDEM - 1 - len(offsets)) # Adiciona valores nulos até a ordem - 1
    pNova.offsets = offsets # Atribui os offsets como os offsets a partir do meio + 1

    filhos = pag.filhos[meio + 1:] # Pega os filhos a partir do meio + 1
    filhos += [NULO] * (ORDEM - len(filhos)) # Adiciona valores nulos até a ordem
    pNova.filhos = filhos  # Atribui os filhos como os filhos a partir do meio + 1

    return chavePro, offsetPro, filhoDpro, pAtual, pNova # Retorna a chave promovida, o offset promovido, o RRN do filho promovido, a página atual e a nova página

def leiaReg(arq) -> tuple[str, int]:

    try:

        tam_bytes = arq.read(2)  # Leia 2 bytes

        if len(tam_bytes) < 2: # Se for menor que 2 bytes retorna vazio

            return '', 0
        
        tam = struct.unpack('h', tam_bytes)[0] # Converte para decimal os bytes

        if tam > 0: # Se o tamanho for maior que 0

            buffer = arq.read(tam) # Faça um read para o tam e decodifique para string

            return buffer.decode('utf-8', errors='replace'), tam
        
    except OSError as e:

        print(f'Erro leia_reg: {e}')

    return '', 0

def buscaNaArvore(chave, rrn, arq):

    if rrn == NULO:  # Condição de parada da recursão

        return False, NULO, NULO
    
    else:

        pag = lePagina(rrn, arq)  # Carrega a página com o RRN dado
        achou, pos = buscaNaPagina(chave, pag)  # Busca a chave na página e obtém a posição

        if achou:

            return True, rrn, pos  # Se a chave foi encontrada, retorna Verdadeiro, rrn e pos
        
        else:

            # Se a chave não foi encontrada na página, busca na página filha
            if pos < len(pag.filhos):  # Verifica se a posição é válida e se há uma página filha na posição

                return buscaNaArvore(chave, pag.filhos[pos], arq)  # Chama recursivamente a busca na página filha
            
            else:

                return False, NULO, NULO  # Se não há uma página filha válida, retorna Falso e NULO
                        
def insereNaArvore(chave, offset, rrnAtual, arq):

    if rrnAtual == NULO:

        chavePro = chave
        offsetPro = offset
        filhoDpro = NULO
        return chavePro, offsetPro, filhoDpro, True
    
    else:

        # leia a página armazenada em rrnAtual para pag
        pag = lePagina(rrnAtual, arq)
        achou, pos = buscaNaPagina(chave, pag)

    if achou:

        raise KeyError("Chave duplicada")
    
    chavePro, offsetPro, filhoDpro, promo = insereNaArvore(chave, offset, pag.filhos[pos], arq)

    if not promo:

        return NULO, NULO, NULO, False
    
    else:

        # se existe um espaco na pag para inserir chave pro 
        if pag.numChaves < ORDEM - 1:

            insereNaPagina(chavePro, offsetPro, filhoDpro, pag)
            escrevePagina(rrnAtual, pag, arq)

            return NULO, NULO, NULO, False
        
        else:

            chavePro, offsetPro, filhoDpro, pAtual, pNova = dividePagina(chavePro, offsetPro, filhoDpro, pag, arq)
            escrevePagina(rrnAtual, pAtual, arq)
            escrevePagina(filhoDpro, pNova, arq)

            return chavePro, offsetPro, filhoDpro, True
                    
# ==============================================================================================