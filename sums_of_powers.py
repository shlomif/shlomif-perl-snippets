#!/usr/bin/env python

# The Expat License
#
# Copyright (c) 2017, Shlomi Fish
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""
sums_of_powers.py - code to search for numbers n, which have two or more
pairs of non-negative integers a, b so that n = a ** e + b ** e for
a certain integral exponent "e".

E.g: test_func(3, 2, 0) finds https://en.wikipedia.org/wiki/1729_%28number%29
because 1729 == 1 ** 3 + 12 ** 3 = 9 ** 3 + 10 ** 3
"""


import heapq
import sys

# from gmpy2 import mpz
# from gmpy_cffi import mpz

from six import print_


class mpz:
    def iroot(x, e):
        high = x
        low = 0
        while high >= low:
            mid = (high + low) >> 1
            if mid ** e < x:
                low = mid + 1
            else:
                high = mid - 1
        while mid ** e < x:
            mid += 1
        while mid ** e > x:
            mid -= 1
        return mid, (mid ** e == x)


class MyIter2:
    def _set_s(self):
        self.s = self.n_pow + self.m ** self.e

    def _set_n(self, n):
        """docstring for _set_n"""
        self.n = n
        self.n_pow = n ** self.e

    def __init__(self, e, n, m=0):
        self.e = e
        self._set_n(n)
        self.m = m
        self._set_s()

    def adv(self):
        if self.m == self.n:
            return False
        self.m += 1
        self._set_s()
        return True

    def n_inc(self):
        self._set_n(self.n + 1)
        self._set_s()

    def clone(self):
        return MyIter2(self.e, self.n, self.m)

    def skip(self, tgt):
        if tgt > (self.n_pow << 1):
            return False
        if tgt == self.s:
            return True
        m, is_exact = mpz.iroot(tgt-self.n_pow, self.e)
        self.m = m + (0 if is_exact else 1)
        self._set_s()
        return True


class IterSumTwo:
    def i(self):
        it = self.it
        return (it.s, it.n, it.clone())

    def __init__(self, e):
        self.q = []
        self.n = 0
        self.e = e
        self.it = MyIter2(e, 0, 0)
        heapq.heappush(self.q, self.i())

    def next(self):
        s, n, i = heapq.heappop(self.q)
        if n == self.n:
            self.n += 1
            self.it.n_inc()
            heapq.heappush(self.q, self.i())
        m = i.m
        if i.adv():
            heapq.heappush(self.q, (i.s, n, i))
        return s, n, m

    def skip(self, tgt):
        q = []
        minn, is_exact = mpz.iroot(tgt >> 1, self.e)
        if not is_exact:
            minn += 1
        maxn, is_exact = mpz.iroot(tgt, self.e)
        if not is_exact:
            maxn -= 1
        e = self.e
        it = MyIter2(e, minn, 0)
        n = minn
        while n <= maxn:
            itc = it.clone()
            self.it = itc
            itc.skip(tgt)
            q.append(self.i())
            it.n_inc()
            n += 1
        self.it = MyIter2(e, maxn, 0)
        self.n = maxn
        heapq.heapify(q)
        self.q = q


def my_iter_func(exponent, wanted_dups_count, start_from):
    it = IterSumTwo(exponent)
    it.skip(start_from)
    c = 0
    prevs = []
    prevs.append(it.next())
    while True:
        c += 1
        if not (c & ((1 << 20) - 1)):
            sys.stderr.write("Reached 0x%X ; %d\n" % (c, prevs[0][0]))
            sys.stderr.flush()
        n = it.next()
        if n[0] == prevs[0][0]:
            prevs.append(n)
        else:
            if len(prevs) >= wanted_dups_count:
                yield ("result", (len(prevs),
                                  prevs[0][0], [(x, y) for z, x, y in prevs]))
            prevs = [n]


def test_func(exponent, wanted_dups_count, start_from):
    fh = open('sums_of_powers.log.txt', 'a')
    it = my_iter_func(exponent, wanted_dups_count, start_from)
    for event in it:
        type_, content = event
        if type_ == "result":
            for f in [fh, sys.stdout]:
                print_(*content, file=f)
                f.flush()


# test_func(3, 2, 0)

test_func(4, 3, 268020050558211886897)
