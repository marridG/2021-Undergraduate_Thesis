import re
import os
import argparse as arg


if __name__ == "__main__":
    template_12f = "(-?\d+\.\d*)," * 11 + "(-?\d+\.\d*)"
    pattern = re.compile(template_12f)
    #listPoses = "/media/lion/Elements SE/Exp0722/csv/"
    #countPos = 0

    # parser = arg.ArgumentParser(description='choose the typical sequence')
    # parser.add_argument('--seq', type=str, default="")
    # args = parser.parse_args()
    # pos = args.seq
    # seqnum = int(args.seq.split('-',1)[0])
    seqnum = 60

    #countPos += 1
    #new_route = "/media/lion/Elements SE/Exp0722/pcd/seq%02d" % seqnum
    # if not os.path.exists(new_route):
    #     os.makedirs(new_route)

    #listCSV = os.listdir(listPoses+pos)
    listCSV = os.listdir("./csv")
    i = 0
    listCSV.sort(key=lambda x: int(x[-9:-5]))
    for file in listCSV:
        i += 1
        lineNumber = 0
        with open("./csv/%s" % (file), 'r') as f:
            with open("processed(frame %04d).txt" % i, "w") as out:
                line = f.readline()
                while line:
                    result_process = pattern.match(line)
                    if result_process:
                        res = result_process.groups()
                        # print(res)
                        formatted = "%.4f %.4f %.4f %.4f\n" % (
                            float(res[0]), float(res[1]), float(res[2]), float(res[3]))
                        out.write(formatted)
                        lineNumber += 1
                    line = f.readline()

        with open("processed(frame %04d).txt" % i, "r") as f:
            with open("./seq%02d/%04d.pcd" % (seqnum, i), "w") as out:
                prompt = '''# .PCD v0.7 - Point Cloud Data file format
VERSION 0.7
FIELDS x y z intensity
SIZE 4 4 4 4
TYPE F F F F
COUNT 1 1 1 1
WIDTH %d
HEIGHT 1
VIEWPOINT 0 0 0 1 0 0 0
POINTS %d
DATA ascii
''' % (lineNumber, lineNumber)
                out.write(prompt)
                line = f.readline()
                while(line):
                    out.write(line)
                    line = f.readline()

        os.remove("processed(frame %04d).txt" % i)
