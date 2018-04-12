#ifndef UTILITY_H
#define UTILITY_H

#define EPSILON 1e-6
#define F_LESS(a, b) ((b) - (a) > EPSILON)
#define F_MORE(a, b) ((a) - (b) > EPSILON)
#define F_EQL(a, b) (!F_LESS((a), (b)) && !F_MORE((a), (b)))


#endif // UTILITY_H
