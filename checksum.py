import argparse
import struct


def sum_range(buffer, start, end):
    sum = 0
    for i in range(start, end, 2):
        sum += struct.unpack_from(">H", data, i)[0]
    return sum

def calculate_ranges(buffer, ranges):
    sum = 0
    for range in ranges:
        print("  range start: " + hex(range[0]) + ", end: " + hex(range[1]))
        sum += sum_range(buffer, range[0], range[1])
    return sum % 2**16

def correct_region(data, region):
    print("Correcting region \"" + region[0] + "\"")
    # Zero checksum word
    offset = region[1]
    data[offset] = 0
    data[offset + 1] = 0

    sum = calculate_ranges(data, region[2])
    # Convert to two's complement
    sum = (0xFFFF ^ sum) + 1

    packed = struct.pack(">H", sum)
    data[offset] = packed[0]
    data[offset + 1] = packed[1]

    new_sum = calculate_ranges(data, region[2])
    if new_sum != 0:
        print("  Checksum correction failed, got " + hex(new_sum) + ", expected 0")
        return False
    else:
        print("  Correction verified")
        return True


def correct(data, regions):
    """Corrects all regions"""
    success = True
    for region in regions:
        if not correct_region(data, region):
            success = False
    return success

def get_regions(data):
    # Get regions from file
    table_addr = 0x514
    regions = [("Main", 0x500, [(0, 0x4000), (0x20000, 0x7FFFD)])]

    region_names = ["Engine Calibration", "Engine Diagnostics", "Transmission Calibration", "Transmission Diagnostics", "Fuel System", "Vehicle System", "VSS"]
    for i in range(0, len(region_names)):
        (start_addr, end_addr) = struct.unpack_from(">LL", data, table_addr + i * 8)
        regions.append((region_names[i], start_addr, [(start_addr, end_addr)]))
    
    return regions

if (__name__ == "__main__"):
    parser = argparse.ArgumentParser(description="Verify checksum of LS1 ROM")
    parser.add_argument("file", type=argparse.FileType("rb"), help="path to ROM")
    parser.add_argument("-v", "--verify", action='store_true')
    parser.add_argument("-c", "--correct", type=argparse.FileType("wb"), metavar="OUTPUT", help='Corrects checksum and writes to OUTPUT')

    args = parser.parse_args()
    file = args.file

    data = file.read()
    file.close()

    regions = get_regions(data)

    if args.verify:
        for region in regions:
            print("Checking region " + region[0])
            sum = calculate_ranges(data, region[2])
            if sum == 0:
                print("Correct")
            else:
                print("Incorrect. Got checksum " + hex(sum))

    elif args.correct != None:
        data = bytearray(data)
        if not correct(data, regions):
            print("WARNING: Failed to correct at least one region")
        else:
            print("All checksums corrected and verified")

        args.correct.write(data)
        args.correct.close()
        
    else:
        parser.print_help()