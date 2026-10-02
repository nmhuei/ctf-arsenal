// Copyright 2026 the V8 project authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef V8_MAGLEV_MAGLEV_STORE_SINK_H_
#define V8_MAGLEV_MAGLEV_STORE_SINK_H_

#include "src/maglev/maglev-basic-block.h"
#include "src/maglev/maglev-graph.h"
#include "src/maglev/maglev-ir.h"

namespace v8::internal::maglev {

class MaglevStoreSink {
 public:
  explicit MaglevStoreSink(Graph* graph)
      : graph_(graph), zone_(graph->zone()) {}

  void Run();

  static constexpr int kSmallFunctionMaxBlocks = 1024;

  Graph* graph() const { return graph_; }
  Zone* zone() const { return zone_; }

 private:
  bool TrySinkIntoLoop(BasicBlock* header);

  Graph* const graph_;
  Zone* const zone_;
};

}  // namespace v8::internal::maglev

#endif  // V8_MAGLEV_MAGLEV_STORE_SINK_H_
