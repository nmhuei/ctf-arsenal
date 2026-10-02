// Copyright 2026 the V8 project authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef V8_MAGLEV_MAGLEV_SMI_CHECK_ELIMINATION_H_
#define V8_MAGLEV_MAGLEV_SMI_CHECK_ELIMINATION_H_

#include "src/maglev/maglev-basic-block.h"
#include "src/maglev/maglev-graph.h"
#include "src/maglev/maglev-ir.h"
#include "src/zone/zone-containers.h"

namespace v8::internal::maglev {

class MaglevSmiCheckElimination {
 public:
  explicit MaglevSmiCheckElimination(Graph* graph);

  void Run();

  Graph* graph() const { return graph_; }
  Zone* zone() const { return zone_; }
  bool is_tracing_enabled() const;

 private:
  static constexpr int kSmallFunctionMaxBlocks = 1024;

  void CollectGuardedIndices();
  void NarrowGuardedUntags();

  Graph* const graph_;
  Zone* const zone_;
  ZoneSet<ValueNode*> guarded_;
};

}  // namespace v8::internal::maglev

#endif  // V8_MAGLEV_MAGLEV_SMI_CHECK_ELIMINATION_H_
