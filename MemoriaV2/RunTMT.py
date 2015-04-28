

class RunTMT():
	def __init__(self, tmtToolPath, xmxarg = None):
		self.prefixCommand = "java7 java -jar "
		if xmxarg != None:
			self.prefixCommand += "-Xmx%s " %xmxarg
		self.tmtToolPath = tmtToolPath

	def step1(self, step1filename):
		print "%s%s %s" %(self.prefixCommand, self.tmtToolPath, step1filename)



runtmt = RunTMT("Tools/tmt-0.4.0.jar")

runtmt.step1("Tools/step1.scala")