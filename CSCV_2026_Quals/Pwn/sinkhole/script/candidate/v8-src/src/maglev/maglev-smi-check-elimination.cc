// Copyright 2026 the V8 project authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "src/maglev/maglev-smi-check-elimination.h"

#include "src/flags/flags.h"
#include "src/maglev/maglev-compilation-info.h"
#include "src/maglev/maglev-ir-inl.h"
#include "src/utils/ostreams.h"

#define TRACE_SCE(msg)                                          \
  if (V8_UNLIKELY(v8_flags.trace_maglev_smi_check_elimination && \
                  is_tracing_enabled())) {                      \
    StdoutStream{} << "[maglev-sce] " << msg << std::endl;      \
  }

namespace v8::internal::maglev {

MaglevSmiCheckElimination::MaglevSmiCheckElimination(Graph* graph)
    : graph_(graph), zone_(graph->zone()), guarded_(graph->zone()) {}

bool MaglevSmiCheckElimination::is_tracing_enabled() const {
  return graph_->compilation_info()->is_tracing_enabled();
}

void MaglevSmiCheckElimination::CollectGuardedIndices() {
  for (BasicBlock* block : graph_->blocks()) {
    for (Node* node : block->nodes()) {
      if (node == nullptr) continue;
      auto* check = node->TryCast<CheckInt32Condition>();
      if (check == nullptr) continue;
      if (check->deoptimize_reason() != DeoptimizeReason::kOutOfBounds) continue;
      if (check->condition() != AssertCondition::kUnsignedLessThan) continue;
      guarded_.insert(check->input(0).node()->UnwrapIdentities());
    }
  }
}

void MaglevSmiCheckElimination::NarrowGuardedUntags() {
  int narrowed = 0;
  for (ValueNode* index : guarded_) {
    if (!index->Is<CheckedObjectToIndex>() && !index->Is<CheckedSmiUntag>()) {
      continue;
    }
    index->OverwriteWith<UnsafeSmiUntag>();
    narrowed++;
  }
  TRACE_SCE("narrowed " << narrowed << " guarded index conversions");
}

void MaglevSmiCheckElimination::Run() {
  if (graph_->num_blocks() <= kSmallFunctionMaxBlocks) return;
  CollectGuardedIndices();
  NarrowGuardedUntags();
}

}  // namespace v8::internal::maglev
