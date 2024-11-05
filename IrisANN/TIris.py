
class TIris ( object ):
  def __init__ ( self ):
    self.InputNodes = 4
    self.EvolvingNodes = 21
    self.OutputNodes = 3
    self.I2EW = [[0.0868056,0.598958,0.0338983,0.0520833],[0.292155,0.835368,0.0742519,0.0353597],[0,0.416667,0.0169492,0],[0.0277778,0.375,0.0677966,0.0416667],[0.153646,0.458984,0.0913665,0.0188802],[0.248318,0.581624,0.100437,0.11263],[0.51796,0.336184,0.657193,0.608349],[0.398003,0.274089,0.476695,0.430339],[0.533854,0.328125,0.753708,0.852865],[0.770942,0.459066,0.81495,0.69987],[0.472222,0.0833333,0.677966,0.583333],[0.520833,0.364583,0.65678,0.708333],[0.527778,0.291667,0.737288,0.5625],[0.472222,0.0833333,0.508475,0.375],[0.194444,0,0.423729,0.375],[0.166667,0.166667,0.389831,0.375],[0.333333,0.15625,0.474576,0.416667],[0.947049,0.555786,0.914642,0.79484],[0.166667,0.208333,0.59322,0.666667],[0.305556,0.416667,0.59322,0.583333],[0.254341,0.405438,0.337138,0.590991]]
    self.E2OW = [[1.11242,0,0],[1.12293,0,0],[1,0,0],[1,0,0],[1.09285,0,0],[1.11192,0,0],[0,1.10733,0],[0,1.07566,0],[0,0,1.05761],[0,0,1.06506],[0,0,1],[0,0,1.02192],[0,0,1.03032],[0,1,0],[0,1,0],[0,1,0],[0,1.03888,0],[0,0,1.08482],[0,0,1],[0,1,0],[0.770013,0.503372,0.197485]]

  def __Satlin ( self, Input ):
    if Input > 1.0:
      return 1.0
    else:
      return Input

  def Recall ( self, InputValues ):
    OutputValues = []
    MaxActivation = 0.0
    Winner = 0
    for CurrEvol in range ( 0, 21 ):
      CurrSum = 0.0
      CurrDiff = 0.0
      for CurrInput in range ( 0, 4 ):
        CurrDiff = CurrDiff + abs ( InputValues [ CurrInput ] - self.I2EW [ CurrEvol] [ CurrInput ] )
        CurrSum  = CurrSum + InputValues [ CurrInput ] + self.I2EW [ CurrEvol ] [ CurrInput ]
      Distance = CurrDiff / CurrSum
      CurrActivation = self.__Satlin ( 1.0 - Distance )
      if CurrActivation > MaxActivation:
        MaxActivation = CurrActivation
        Winner = CurrEvol

    for CurrOutput in range ( 0, 3 ):
      OutVal = self.__Satlin ( MaxActivation * self.E2OW [ Winner ] [ CurrOutput ] )
      OutputValues.append ( OutVal )
    
    return OutputValues

