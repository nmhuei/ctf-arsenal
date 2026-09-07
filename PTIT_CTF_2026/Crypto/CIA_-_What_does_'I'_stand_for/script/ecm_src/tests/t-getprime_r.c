/* Tests for getprime_r.c

Copyright 2026 Seth Troisi.

This file is part of the ECM Library.

The ECM Library is free software; you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation; either version 2.1 of the License, or (at your
option) any later version.

The ECM Library is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
License for more details.

You should have received a copy of the GNU Lesser General Public License
along with the ECM Library; see the file COPYING.LIB.  If not, write to
the Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston,
MA 02110-1301, USA.
*/

#include <assert.h>
#include <stdio.h>

#include "getprime_r.h"


int main() {
  prime_info_t prime_info;

  /* Test getprime_last_prime is initially equal to 0. */
  prime_info_init (prime_info);
  assert (getprime_last_prime (prime_info) == 0);

  double test_limit = 1000;

  /* Test getprime_last_prime returns the mostly recently returned prime. */
  double p = getprime_mt (prime_info);
  for (; p <= test_limit; p = (double) getprime_mt (prime_info))
    {
        assert (getprime_last_prime (prime_info) == p);
    }

  /* Test large jumping forward. */
  p = getprime_jump_and_next_mt (prime_info, 10007);
  assert( p == 10007 );
  assert (getprime_last_prime (prime_info) == p);

  /* Test jumping one after current prime. */
  p = getprime_jump_and_next_mt (prime_info, 10008);
  assert( p == 10009 );
  assert (getprime_last_prime (prime_info) == p);

  /* Test jumping to current prime. */
  p = getprime_jump_and_next_mt (prime_info, 10009);
  assert( p == 10009 );
  assert (getprime_last_prime (prime_info) == p);

  /* Test jumping backwards. */
  p = getprime_jump_and_next_mt (prime_info, 10);
  assert( p == 11 );
  assert (getprime_last_prime (prime_info) == p);

  /* Test jumping backwards to 0 */
  p = getprime_jump_and_next_mt (prime_info, 0);
  assert( p == 3 );
  assert (getprime_last_prime (prime_info) == p);

  return 0;
}
