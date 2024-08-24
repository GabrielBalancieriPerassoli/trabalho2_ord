import struct

# Constantes
ORDEM = 5
NULO = -1
FORMATO_PAG = f'i{ORDEM - 1}i{ORDEM - 1}i{ORDEM}i'
TAM_PAG = struct.calcsize(FORMATO_PAG)
FORMATO_CAB = 'i'
TAM_CAB = struct.calcsize(FORMATO_CAB)
ARQ_GAMES = 'games.dat'
ARQ_BTREE = 'btree.dat'