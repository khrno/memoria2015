CC = g++
CFLAGS = -Wno-deprecated -std=c++11 -O3
LDFLAGS = -lm
INC=-I/usr/local/Cellar/boost/1.57.0/
LIB = csv.h FormalContext.hpp

default: run

FormalContext.o: FormalContext.cpp ${LIB}
	${CC} ${CFLAGS} $(INC) -c FormalContext.cpp

main.o: main.cpp ${LIB}
	${CC} ${CFLAGS} $(INC) -c main.cpp

main: main.o FormalContext.o
	${CC} ${CFLAGS} $(INC) FormalContext.o main.o -o main

run: main
	./main

clean:
	rm -rf main main.o FormalContext.o