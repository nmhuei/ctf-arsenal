import subprocess, tempfile

# We will run chrome on a minimal HTML that warms up a function with > 1024 blocks.
# Let's inspect MaglevStoreSink::Run in GDB!

gdb_script = """
set pagination off

b v8::internal::maglev::MaglevStoreSink::Run
commands
  silent
  printf "=== MaglevStoreSink::Run on graph: %p (num_blocks=%d) ===\\n", graph_, graph_->num_blocks()
  set $blocks = graph_->blocks()
  set $i = 0
  set $n = graph_->num_blocks()
  while $i < $n
    set $b = $blocks.data_[$i]
    if $b != 0 && $b->is_loop_
      printf "Found loop block %d: preds=%d\\n", $b->id_, $b->predecessor_count_
      if $b->predecessor_count_ == 2
        set $p = $b->predecessors_.data_[0]
        printf "  Preheader %d: nodes=%d\\n", $p->id_, $p->nodes_.size_
        set $j = 0
        while $j < $p->nodes_.size_
          set $node = $p->nodes_.data_[$j]
          if $node != 0
            printf "    node %d: opcode=%d\\n", $j, $node->opcode_
          end
          set $j = $j + 1
        end
      end
    end
    set $i = $i + 1
  end
  continue
end

run
quit
"""

with open("script/gdb_sink_detail.txt", "w") as f:
    f.write(gdb_script)

