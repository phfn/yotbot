#!/usr/bin/python3
import socket
from array import array
from struct import unpack, pack
from math import ceil

__all__ = ["client", 'fc']

def fc():
    print("Supported Function Codes:\n\
            1 = Read Coils or Digital Outputs\n\
            2 = Read Digital Inputs\n\
            3 = Read Holding Registers\n\
            4 = Read Input Registers\n\
            5 = Write Single Coil\n\
            6 = Write Single Register\n\
            15 = Write Coils or Digital Outputs\n\
            16 = Write Holding Registers")

class client:
    def __init__(self, host='localhost', unit=1):
        self.host = host
        self.unit = unit
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, 502))
        self.TID = 0

    def read(self, FC=4, ADR=0, LEN=10): #Default Read: Input Registers
        if FC not in [1,2,3,4]: return(fc())
        lADR = ADR & 0x00FF
        mADR = ADR >> 8
        lLEN = LEN & 0x00FF
        mLEN = LEN >> 8
        if (FC < 3):
            BYT = ceil(LEN / 8)  # Round off the no. of bytes
        else:
            BYT = LEN * 2
        if self.TID < 255: 
            self.TID = self.TID + 1
        else: self.TID = 1
        cmd = array('B', [0, self.TID, 0, 0, 0, 6,
            self.unit, FC, mADR, lADR, mLEN, lLEN])
        self.sock.send(cmd)
        buf = array('B', [0] * (BYT + 9))
        self.sock.recv_into(buf)
        if (FC > 2):
            return unpack('>' + 'H' * LEN, buf[9:(9 + BYT)])
        else:
            return unpack('B' * BYT, buf[9:(9 + BYT)])

    @staticmethod
    def merge_register(registers: tuple, register_size=16):
        """Merge s tuple of regster values (as ints) to a single int.
        Example:
            merge_register((0b11110000, 0b10101010))
            0b1111000010101010
        """
        res = 0
        for i, register in enumerate(registers):
            if register.bit_length() > register_size:
                raise Exception(f"Register is bigger than register size: len({bin(register)})>{register_size}")
            res = (register << (register_size*(len(registers)-i-1))) | res
        return res

    def read_and_merge(self, FC=4, ADR=0, LEN=10):
        """Read multiple registers and returns them a 1 single int
        See also:
            read()
            merge_register()
        """
        values = self.read(FC, ADR, LEN)
        return client.merge_register(values)

    def read_string(self, FC=4, ADR=0, LEN=0, n_bits=8):
        """Read multiple registers and returns them a 1 String.
        By default, it converts splitting in chunks of 8 bits an convert them to chars.
        Change n_bits if your text is encoded in chunks of 7 bit.
        See also:
            read_and_merge()
        """
        value = self.read_and_merge(FC, ADR, LEN)
        value_bin = bin(value)[2:]
        s = ""
        #split the binary data to chunks of 8, and convert them to chars
        for i in range(0, len(value_bin), n_bits):
            bits = value_bin[i:i+7]
            bits_int = int(bits, 2)
            if bits_int == 0:
                continue
            bits_char = chr(bits_int)
            s += bits_char
        return s

    def write(self, *DAT, FC=16, ADR=0): #Default Write: Holding Registers
        if FC not in [5,6,15,16]: return(fc())
        lADR = ADR & 0x00FF
        mADR = ADR >> 8
        VAL = b''
        for i in DAT:
            VAL = VAL + pack('>H', i)
        if FC == 5 or FC == 6:
            VAL = VAL[0:2]			 
        if FC == 5 or FC == 15:
            LEN = len(VAL) * 8
        else:
            LEN = len(VAL) // 2
        lLEN = LEN & 0x00FF
        mLEN = LEN >> 8
        if self.TID < 255: 
            self.TID = self.TID + 1
        else: self.TID = 1
        if FC == 6:
            cmd = array('B', [0, self.TID, 0, 0, 0, 6, self.unit, FC, mADR, lADR])
        else:
            cmd = array('B', [0, self.TID, 0, 0, 0, 7 + len(VAL), self.unit, FC, mADR, lADR, mLEN, lLEN, len(VAL)])
        cmd.extend(VAL)
        buffer = array('B', [0] * 20)
        print("Sent", cmd)
        self.sock.send(cmd)
        self.sock.recv_into(buffer)
