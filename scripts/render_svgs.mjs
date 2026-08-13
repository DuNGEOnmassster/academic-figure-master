#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
let sharp;
try {
  sharp = require("sharp");
} catch (error) {
  console.error("The optional paper-calibration renderer needs the 'sharp' package.");
  console.error("Install it with `npm install --no-save sharp`, then rerun this script.");
  process.exit(2);
}

const [inputDirectory = "assets/paper-redraws", outputDirectory = "tmp/paper-calibration/redraws", densityValue = "220"] = process.argv.slice(2);
const density = Number.parseInt(densityValue, 10);
if (!Number.isFinite(density) || density < 72) {
  console.error(`Invalid SVG render density: ${densityValue}`);
  process.exit(2);
}
fs.mkdirSync(outputDirectory, { recursive: true });

const files = fs.readdirSync(inputDirectory).filter((name) => name.endsWith(".svg")).sort();
for (const name of files) {
  const input = path.join(inputDirectory, name);
  const output = path.join(outputDirectory, name.replace(/\.svg$/, ".png"));
  await sharp(input, { density }).flatten({ background: "white" }).png().toFile(output);
  console.log(output);
}
