CC=g++
CXXFLAGS=-O3 -g3 -fno-pie -lprofiler -ltcmalloc
CXXFLAGS+= -fno-builtin-malloc -fno-builtin-calloc -fno-builtin-realloc -fno-builtin-free

DEPS=src/scheduler/cpp/data.cpp src/scheduler/cpp/types/*.cpp

bin/exhaustive: src/scheduler/cpp/exhaustive_search.cpp ${DEPS}
	${CC} -std=c++0x ${CXXFLAGS} $^ -o $@

bin/stem_search: src/scheduler/cpp/stem_search.cpp ${DEPS}
	${CC} -std=c++14 ${CXXFLAGS} $^ -o $@
