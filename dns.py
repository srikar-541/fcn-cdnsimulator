#!/usr/bin/env python3
import socket
import sys, getopt

def getFlags(flags):
    byte1 = bytes(flags[:1])
    QR = '1'
    OPCODE = ''
    for bit in range(1, 5):
        OPCODE += str(ord(byte1) & (1 << bit))
    # pass
    AA = '1'
    TC = '0'
    RD = '0'
    RA = '0'
    Z = '000'
    RCODE = '0000'

    return int(QR + OPCODE + AA + TC + RD, 2).to_bytes(1, byteorder='big') \
           + int(RA + Z + RCODE, 2).to_bytes(1, byteorder='big')


def getQuestion(data):
    state = 0
    expectedLength = 0
    domainPart = ''
    domainParts = []
    x = 0
    y = 0
    for byte in data:
        if state == 1:
            if byte != 0:
                domainPart += chr(byte)
            x += 1
            if x == expectedLength:
                domainParts.append(domainPart)
                domainPart = ''
                state = 0
                x = 0
            if byte == 0:
                domainParts.append(domainPart)
                break
        else:
            state = 1
            expectedLength = byte
        y += 1

    questionType = data[y:y + 2]

    return domainParts, questionType


def getrecs(data):
    domain, questiontype = getQuestion(data)
    qt = ''
    if questiontype == b'\x00\x01':
        qt = 'a'
    return  qt, domain


def rectobytes(rectype, recttl, recval):
    rbytes = b'\xc0\x0c'

    if rectype == 'a':
        rbytes = rbytes + bytes([0]) + bytes([1])

    rbytes = rbytes + bytes([0]) + bytes([1])

    rbytes += int(recttl).to_bytes(4, byteorder='big')

    if rectype == 'a':
        rbytes = rbytes + bytes([0]) + bytes([4])

        for part in recval.split('.'):
            rbytes += bytes([int(part)])
    return rbytes


def buildquestion(domainname, rectype):
    qbytes = b''

    for part in domainname:
        length = len(part)
        qbytes += bytes([length])

        for char in part:
            qbytes += ord(char).to_bytes(1, byteorder='big')

    if rectype == 'a':
        qbytes += (1).to_bytes(2, byteorder='big')

    qbytes += (1).to_bytes(2, byteorder='big')

    return qbytes


def build_dns_response(data):
    transactionId = data[:2]

    Flags = getFlags(data[2:4])

    QDCOUNT = b'\x00\x01'

    ANCOUNT = b'\x00\x01'

    NSCOUNT = (0).to_bytes(2, byteorder='big')

    ARCOUNT = (0).to_bytes(2, byteorder='big')

    dnsHeader = transactionId + Flags + QDCOUNT + ANCOUNT + NSCOUNT + ARCOUNT

    rectype, domainname = getrecs(data[12:])
    dnsQuestion = buildquestion(domainname, rectype)

    d = '.'.join(domainname[:-1])
    if d == 'cs5700cdn.example.com':
        d = 'cs5700cdnproject.ccs.neu.edu'
    dnsBody = b''
    dnsBody += rectobytes(rectype, '400', socket.gethostbyname(d))

    return dnsHeader + dnsQuestion + dnsBody


def main(argv):
   port = ''
   name = ''
   try:
      opts, args = getopt.getopt(argv,"p:n:")
   except getopt.GetoptError:
      print ('./dnsserver -p <port> -n <name>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print ('./dnsserver -p <port> -n <name>')
         sys.exit()
      elif opt == "-p":
         port = int(arg)
         if port < 40000 or port > 65535:
             print("Please enter the port number between 40000 and 65000")
             sys.exit()
      elif opt == "-n":
         name = arg
   if port == '' or name == '':
       print('./dnsserver -p <port> -n <name>')
       sys.exit()

   ip = '0.0.0.0'
   # port = 53
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   s.bind((ip, port))

   while 1:
       data, addr = s.recvfrom(512)
       resp = build_dns_response(data)
       s.sendto(resp, addr)


if __name__ == "__main__":
   main(sys.argv[1:])
