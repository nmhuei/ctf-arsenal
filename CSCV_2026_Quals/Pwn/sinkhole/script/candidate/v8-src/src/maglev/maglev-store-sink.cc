// Copyright 2026 the V8 project authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "src/maglev/maglev-store-sink.h"

#include "src/flags/flags.h"
#include "src/maglev/maglev-ir-inl.h"

namespace v8::internal::maglev {

namespace {
bool IsSinkableTransition(Node* node) {
  return node->Is<TransitionElementsKindOrCheckMap>() ||
         node->Is<TransitionElementsKind>();
}
bool IsElementStore(Node* node) {
  return node->Is<StoreFixedArrayElementWithWriteBarrier>() ||
         node->Is<StoreFixedArrayElementNoWriteBarrier>();
}
}  // namespace

bool MaglevStoreSink::TrySinkIntoLoop(BasicBlock* header) {
  if (!header->is_loop()) return false;
  if (header->predecessor_count() != 2) return false;
  BasicBlock* preheader = header->predecessor_at(0);
  if (preheader->successors().size() != 1) return false;
  auto* entry = preheader->control_node()->TryCast<CheckpointedJump>();
  if (entry == nullptr) return false;

  ZoneVector<Node*>& pn = preheader->nodes();
  int from = -1, to = -1;
  for (int i = 0; i < static_cast<int>(pn.size()); i++) {
    if (pn[i] == nullptr) continue;
    if (IsSinkableTransition(pn[i])) from = i;
    if (from >= 0 && IsElementStore(pn[i])) {
      to = i;
      break;
    }
  }
  if (from < 0 || to < 0) return false;

  for (int i = from; i <= to; i++) {
    Node* n = pn[i];
    if (n == nullptr) continue;
    if (n->properties().has_eager_deopt_info()) {
      n->CopyEagerDeoptInfoOf(entry, zone_);
    }
    n->set_owner(header);
    header->nodes().push_back(n);
    pn[i] = nullptr;
  }
  return true;
}

void MaglevStoreSink::Run() {
  if (graph_->num_blocks() <= kSmallFunctionMaxBlocks) return;
  for (BasicBlock* block : graph_->blocks()) {
    if (block == nullptr) continue;
    TrySinkIntoLoop(block);
  }
}

}  // namespace v8::internal::maglev
