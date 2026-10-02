// Copyright 2026 the V8 project authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef V8_EXTENSIONS_CAGE_BASE_EXTENSION_H_
#define V8_EXTENSIONS_CAGE_BASE_EXTENSION_H_

#include "include/v8-extension.h"
#include "include/v8-local-handle.h"

namespace v8 {

template <typename T>
class FunctionCallbackInfo;

namespace internal {

// Exposes the base address of the pointer-compression cage as
// |cageBase()|, so that compressed pointers reported by the various tracing
// flags can be resolved to absolute addresses from script.
//
// Only installed when --expose-cage-base is passed.
class CageBaseExtension : public v8::Extension {
 public:
  CageBaseExtension()
      : v8::Extension("v8/cage-base", "native function cageBase();") {}
  v8::Local<v8::FunctionTemplate> GetNativeFunctionTemplate(
      v8::Isolate* isolate, v8::Local<v8::String> name) override;
  static void CageBase(const v8::FunctionCallbackInfo<v8::Value>& info);
};

}  // namespace internal
}  // namespace v8

#endif  // V8_EXTENSIONS_CAGE_BASE_EXTENSION_H_
