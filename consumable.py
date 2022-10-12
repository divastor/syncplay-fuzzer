class ConsumableException(Exception):
    pass
class Consumable:
    def __init__(self, buf):
        self.buf = buf
        self.index = 0
        self.bool_val = -1
        self.bool_being_consumed = 0
        self.bool_index = 0
        self.len = len(buf)

    def remainingBytes(self):
        return self.len - self.index
    def getInt(self):
        if self.remainingBytes() < 4:
            raise ConsumableException("Consumable length exceeded for int.")
        
        i = int.from_bytes(self.buf[self.index:self.index+4],'little')
        self.index += 4

        return i

    def getByte(self):
        if self.len-1 < self.index:
            raise ConsumableException("Consumable length exceeded for byte.")
        
        b = self.buf[self.index]
        self.index += 1

        return b

    def getBool(self):
        if self.bool_index == 8:
            # assign current byte as consumable bool
            self.bool_val = self.getByte()
            self.bool_being_consumed = self.index
            self.bool_index = 0
            self.index += 1 # move index to next byte
        
        # bit fiddling to get the bit of bool_index
        b = (self.bool_val >> self.bool_index) & 0b1 
        self.bool_index += 1

        return bool(b)

    def getString(self):
        s_length = self.getByte()
        if s_length == 0:
            return ""
        
        s = self.buf[self.index + 1 : self.index + 1 + s_length]
        self.index += s_length + 1

        return s.decode('utf-8')