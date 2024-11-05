import string
import sys

import TIris

TestFileName = sys.argv[1]  # name/path of the data file

# load the data file into memory for parsing
TestFile = open(TestFileName)
Test = TestFile.readlines()
TestFile.close()

# instantiate the ANN class TIris as object TheNetwork
TheNetwork = TIris.TIris()

# loop over the test data file one line at a time
for CurrLine in Test:
    # split the line into tokens
    CurrLine = CurrLine.strip()
    Tokens = CurrLine.split(",")
    InputVector = []

    # convert the tokens into float values
    # and enter them into a vector
    for CurrTok in Tokens:
        InVal = float(CurrTok)
        InputVector.append(InVal)

    # recall the ANN with the vector
    Output = TheNetwork.Recall(InputVector)

    # convert the output vector to a string
    OutputString = ""
    for CurrOut in Output:
        OutputString = OutputString + str(CurrOut) + " "
    OutputString = OutputString + "\n"

    # write the outputs to the console
    print(OutputString.strip())
