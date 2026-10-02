// Copyright 2026 the V8 project authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "src/extensions/cage-base-extension.h"

#include "include/v8-isolate.h"
#include "include/v8-primitive.h"
#include "include/v8-template.h"
#include "src/execution/isolate.h"
#include "src/handles/handles.h"

namespace v8::internal {

v8::Local<v8::FunctionTemplate> CageBaseExtension::GetNativeFunctionTemplate(
    v8::Isolate* isolate, v8::Local<v8::String> str) {
  return v8::FunctionTemplate::New(isolate, CageBaseExtension::CageBase);
}

void CageBaseExtension::CageBase(
    const v8::FunctionCallbackInfo<v8::Value>& info) {
  Isolate* isolate = reinterpret_cast<Isolate*>(info.GetIsolate());
  info.GetReturnValue().Set(v8::Number::New(
      info.GetIsolate(), static_cast<double>(isolate->cage_base())));
}

}  // namespace v8::internal
