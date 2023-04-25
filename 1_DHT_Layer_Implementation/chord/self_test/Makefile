CXX = g++
CPPFLAGS =
CXXFLAGS = -std=c++17 -Wall

.default: all

all: chord

chord: ../self_test/src/chord.cc src/chord.h src/rpcs_test.h
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -pthread -o chord ../self_test/src/chord.cc -lrpc

clean:
	$(RM) chord
