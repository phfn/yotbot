#!/usr/bin/python3
import socket
from array import array
from struct import unpack, pack
from math import ceil
from numpy import uint32

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
    def __init__(self, host='localhost', port=502, unit=1):
        self.host = host
        self.port = port
        self.unit = unit
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.TID = 0

    def __enter__(self):
        self.sock.connect((self.host, self.port))
        return self

    def __exit__(self, exc_type, exc_val: Exception, taceback):
        self.sock.close()
        if exc_val:
            raise exc_val

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
        """Read multiple registers and returns them a 1 single unsigned int
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
        bin_str = self.read_bin(FC, ADR, LEN)
        s = ""
        #split the binary data to chunks of 8, and convert them to chars
        for i in range(0, len(bin_str), n_bits):
            bits = bin_str[i:i+n_bits]
            bits_int = int(bits, 2)
            if bits_int == 0:
                continue
            bits_char = chr(bits_int)
            s += bits_char
        return s

    @staticmethod
    def _decode_from_twos_complement(bits: int):
        bits = uint32(bits)
        if (1 << 32 -1) & bits != 0:
            # if the highest bit is set, value is negativ
            bits = uint32(bits -1)
            bits = uint32(~bits)
            return -int(bits)


    def read_int(self, FC=4, ADR=1, LEN=10):
        """Read multiple registers and returns them a 1 single signed int.
        Works only on 32 bit
        See also:
            read()
            merge_register()
        """
        uint = uint32(self.read_and_merge(FC, ADR, LEN))
        if (1 << 31) & uint != 0:
            # if the highest bit decode_from_twos_complementis set, value is negativ
            return self._decode_from_twos_complement(uint)
        return uint

    def read_float(self, FC=4, ADR=1, LEN=10):
        """Read multiple registers and returns them a 1 single float.
        Bits get converted by IEEE754
        Works only on 32 bit
        See also:
            read()
            merge_register()
        """
        bin_str = self.read_bin(FC, ADR, LEN)
        if bin_str == f"{0:032b}":
            return 0
        sign = int(bin_str[0])
        exponent = int(bin_str[1:9],2)
        mantisse = int("1"+bin_str[9:], 2)
        shift =  len(bin_str)-9 - (exponent-127) 

        return ((-1)**sign) * mantisse /( 1<<(shift))

    def read_bin(self, FC=4, ADR=1, LEN=10) -> str:
        """Read multiple registers and returns them a 1 binary string.
        See also:
            read()
            merge_register()
        """
        bit_length = LEN*16
        value = self.read_and_merge(FC, ADR, LEN)
        return f"{value:0{bit_length}b}"


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
