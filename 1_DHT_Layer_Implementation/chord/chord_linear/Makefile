CXX = g++
CPPFLAGS =
CXXFLAGS = -std=c++17 -Wall

.default: all

all: chord

chord: ../chord_linear/src/chord.cc src/chord.h src/rpcs_linear.h
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -pthread -o chord ../chord_linear/src/chord.cc -lrpc

clean:
	$(RM) chord
