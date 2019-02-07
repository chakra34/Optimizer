#!/usr/bin/env python
# -*- coding: UTF-8 no BOM -*-

#     __ __ __________  ____  __ ____  ______  ____
#    / //_// ____/ __ \/ __ \/ //_/ / / / __ \/ __ \
#   / ,<  / __/ / / / / / / / ,< / / / / / / / / / /
#  / /| |/ /___/ /_/ / /_/ / /| / /_/ / /_/ / /_/ /
# /_/ |_/_____/_____/\____/_/ |_\____/_____/\____/

#######################################
# Convert Excel Workbook to Text File #
#######################################

import sys,string,xlrd

fname = sys.argv[1]
xl_workbook = xlrd.open_workbook(fname)

for sheet in xl_workbook.sheets()[2:-1]:
  print sheet.name
  with open(string.replace(sheet.name,' ','_')+'.txt',"w") as output:
    output.write("1 head\n")
    output.write("\t".join([string.replace(str(sheet.cell(0,col).value)," ","_")+ \
                            '/' + \
                            str(sheet.cell(1,col).value) \
                            for col in xrange(sheet.ncols-6,sheet.ncols)])+"\n")
    for row in xrange(2,sheet.nrows):
      output.write("\t".join([string.replace(str(sheet.cell(row,col).value)," ","_") for col in xrange(sheet.ncols-6,sheet.ncols)])+"\n")
