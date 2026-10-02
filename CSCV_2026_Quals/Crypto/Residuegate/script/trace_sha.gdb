set pagination off
set $hits = 0
break *0x5596dd70e070
commands 1
  silent
  set $hits = $hits + 1
  printf "HIT %d rdi=%p rsi=%p rdx=%d\n", $hits, $rdi, $rsi, $rdx
  x/96bx $rsi
  if $hits >= 12
    disable 1
  else
    continue
  end
end
continue
bt 12
detach
