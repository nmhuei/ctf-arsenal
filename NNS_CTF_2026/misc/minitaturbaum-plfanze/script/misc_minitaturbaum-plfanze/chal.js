"use strict";

import { bonsai } from "bonsai-js";
import { all } from "bonsai-js/stdlib";

const code = process.argv[2];
const expr = bonsai().use(all);
expr.evaluate(code, {});
