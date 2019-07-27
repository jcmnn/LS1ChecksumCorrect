import argparse
import struct


def sum_range(buffer, start, end):
    sum = 0
    for i in range(start, end, 2):
        sum += struct.unpack_from(">H", data, i)[0]
    return sum

def calculate(buffer):
    sum = sum_range(buffer, 0, 0x4000) + sum_range(buffer, 0x20000, 0x7FFFD)
    sum = sum % 2**16
    return sum

if (__name__ == "__main__"):
    parser = argparse.ArgumentParser(description="Verify checksum of LS1 ROM")
    parser.add_argument("file", type=argparse.FileType("rb"), help="path to ROM")
    parser.add_argument("-v", "--verify", action='store_true')
    parser.add_argument("-c", "--correct", type=argparse.FileType("wb"), metavar="OUTPUT", help='Corrects checksum and writes to OUTPUT')

    args = parser.parse_args()
    file = args.file

    data = file.read()
    file.close()

    if args.verify:
        sum = calculate(data)
        if sum == 0:
            print("Correct")
        else:
            print("Incorrect. Got checksum " + hex(sum))
    elif args.correct != None:
        sum = sum_range(data, 0, 0x500) + sum_range(data, 0x502, 0x4000) + sum_range(data, 0x20000, 0x7FFFD)
        sum = sum % 2**16

        data = bytearray(data)

        # Convert to two's complement
        sum = (0xFFFF ^ sum) + 1

        packed = struct.pack(">H", sum)
        data[0x500] = packed[0]
        data[0x501] = packed[1]

        new_sum = calculate(data)
        if new_sum != 0:
            print("Checksum correction failed, got " + hex(new_sum) + ", expected 0")
        else:
            args.correct.write(data)
            args.correct.close()
            print("Corrected checksum")
    else:
        parser.print_help()