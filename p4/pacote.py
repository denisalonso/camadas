import os


class Pacote(object):
    def __init__(self):
        self.EOP = b'\xAF\x8E\xFF\x02'
        self.hdr_len = 10

        self.HELLO =    1
        self.ACK =      2
        self.PAUSE =    3
        self.ABORT =    4
        self.FIN =      5
    
    def cria_header(self, tipo, id, crc, ):


    def empacotar(self,caminho):
        pass