# Minimal Phantasmoon bot: catch the nearest moonwisp, return it to the
# player's Moon Gate, and repeat.

.equ MMIO_VELOCITY, 0xffff0000
.equ MMIO_HEADING, 0xffff0004
.equ MMIO_SELF_X, 0xffff0008
.equ MMIO_SELF_Y, 0xffff000c
.equ MMIO_MOONLIGHT, 0xffff0020
.equ MMIO_SCAN_WISPS, 0xffff0040
.equ MMIO_CATCH_WISP, 0xffff0044
.equ MMIO_DEPOSIT_WISPS, 0xffff0048
.equ MMIO_CARRIED_COUNT, 0xffff0054
.equ MMIO_OWN_GATE, 0xffff005c
.equ MMIO_ATTACK, 0xffff006c

.equ ATTACK_STUN, 1
.equ ATTACK_KNOCKBACK, 2

.equ WISP_SLOT_SIZE, 24
.equ ARRIVAL_TOLERANCE, 16
.equ WISP_SCAN_SIZE, 292

.section .text.init, "ax", @progbits
.global _start
.type _start, @function
_start:
  li s1, MMIO_VELOCITY
  la s0, wisp_scan
  lw t0, MMIO_OWN_GATE - MMIO_VELOCITY(s1)
  srli s5, t0, 16
  slli s6, t0, 16
  srli s6, s6, 16

main_loop:
  lw t0, MMIO_CARRIED_COUNT - MMIO_VELOCITY(s1)
  bnez t0, return_home
  lw t0, MMIO_MOONLIGHT - MMIO_VELOCITY(s1)
  beqz t0, idle

  sw s0, MMIO_SCAN_WISPS - MMIO_VELOCITY(s1)
  lw a0, 0(s0)
  addi a1, s0, 4
  li a2, 0
  li a3, 0x7fffffff
  li s2, -1
  lw a4, MMIO_SELF_X - MMIO_VELOCITY(s1)
  lw a5, MMIO_SELF_Y - MMIO_VELOCITY(s1)

find_nearest:
  beq a2, a0, target_selected
  lw t0, 4(a1)
  sub t1, t0, a4
  bgez t1, x_distance
  neg t1, t1

x_distance:
  lw t2, 8(a1)
  sub t3, t2, a5
  bgez t3, y_distance
  neg t3, t3

y_distance:
  add t1, t1, t3
  bge t1, a3, next_wisp
  mv a3, t1
  lw s2, 0(a1)
  mv s3, t0
  mv s4, t2

next_wisp:
  addi a1, a1, WISP_SLOT_SIZE
  addi a2, a2, 1
  j find_nearest

target_selected:
  li t0, -1
  beq s2, t0, main_loop

navigate_wisp:
  lw t0, MMIO_SELF_X - MMIO_VELOCITY(s1)
  sub t1, s3, t0
  li t2, ARRIVAL_TOLERANCE
  bgt t1, t2, move_east
  neg t2, t2
  blt t1, t2, move_west

  lw t0, MMIO_SELF_Y - MMIO_VELOCITY(s1)
  sub t1, s4, t0
  li t2, ARRIVAL_TOLERANCE
  bgt t1, t2, move_south
  neg t2, t2
  blt t1, t2, move_north

  sw zero, 0(s1)
  sw s2, MMIO_CATCH_WISP - MMIO_VELOCITY(s1)
  j main_loop

return_home:
  mv s3, s5
  mv s4, s6

navigate_home:
  lw t0, MMIO_SELF_X - MMIO_VELOCITY(s1)
  sub t1, s3, t0
  li t2, ARRIVAL_TOLERANCE
  bgt t1, t2, home_east
  neg t2, t2
  blt t1, t2, home_west

  lw t0, MMIO_SELF_Y - MMIO_VELOCITY(s1)
  sub t1, s4, t0
  li t2, ARRIVAL_TOLERANCE
  bgt t1, t2, home_south
  neg t2, t2
  blt t1, t2, home_north

  sw zero, 0(s1)
  lw t0, MMIO_CARRIED_COUNT - MMIO_VELOCITY(s1)
  sw t0, MMIO_DEPOSIT_WISPS - MMIO_VELOCITY(s1)
  j main_loop

move_east:
  li t0, 0
  j move
move_south:
  li t0, 90
  j move
move_west:
  li t0, 180
  j move
move_north:
  li t0, 270
move:
  sw t0, MMIO_HEADING - MMIO_VELOCITY(s1)
  li t0, 10
  sw t0, 0(s1)
  j navigate_wisp

home_east:
  li t0, 0
  j move_home
home_south:
  li t0, 90
  j move_home
home_west:
  li t0, 180
  j move_home
home_north:
  li t0, 270
move_home:
  sw t0, MMIO_HEADING - MMIO_VELOCITY(s1)
  li t0, 10
  sw t0, 0(s1)
  j navigate_home

idle:
  sw zero, 0(s1)
  j idle
.size _start, . - _start

.section .bss
.balign 4
wisp_scan:
  .zero WISP_SCAN_SIZE
