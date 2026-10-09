// Exporta título, cor e path dos Simple Icons (CC0) usados pelo stack.py e buttons.py.
import * as icons from "simple-icons";
import { writeFileSync } from "node:fs";
const out = {};
for (const [k, v] of Object.entries(icons)) if (k.startsWith("si")) out[v.slug] = { t: v.title, h: v.hex, p: v.path };
writeFileSync(new URL("./icons.json", import.meta.url), JSON.stringify(out));
console.log(`${Object.keys(out).length} ícones exportados`);
