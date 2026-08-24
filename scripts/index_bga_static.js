#!/usr/bin/env node
'use strict';

const fs = require('fs');
const vm = require('vm');

const path = process.argv[2];
const outputPath = process.argv[3];
if (!path) {
  throw new Error('usage: index_bga_static.js <source.js> [output.json]');
}
const src = fs.readFileSync(path, 'utf8');
const names = [...src.matchAll(/^const\s+([A-Za-z_$][\w$]*)\s*=/gm)].map((match) => match[1]);
const transformed = src.replace(/^const\s+([A-Za-z_$][\w$]*)\s*=/gm, 'globalThis.$1 =');
const context = {};
vm.createContext(context);
vm.runInContext(transformed, context, { timeout: 10000 });

function* flattenStrings(value) {
  if (typeof value === 'string') {
    yield value;
  } else if (Array.isArray(value)) {
    for (const item of value) yield* flattenStrings(item);
  } else if (value && typeof value === 'object') {
    for (const item of Object.values(value)) yield* flattenStrings(item);
  }
}

const result = { source: path, topLevelConstantCount: names.length, tables: [] };
for (const name of names) {
  const value = context[name];
  const kind = Array.isArray(value) ? 'array' : value === null ? 'null' : typeof value;
  let count = null;
  let keys = [];
  let fieldKeys = [];
  let fieldTypes = {};
  let placeholderTokens = [];
  if (Array.isArray(value)) {
    count = value.length;
    keys = value.slice(0, 20).map((_, index) => String(index));
  } else if (value && typeof value === 'object') {
    keys = Object.keys(value);
    count = keys.length;
    const fields = new Set();
    const types = {};
    const placeholders = new Set();
    for (const record of Object.values(value)) {
      if (!record || typeof record !== 'object') continue;
      for (const [key, item] of Object.entries(record)) {
        fields.add(key);
        const type = Array.isArray(item) ? 'array' : item === null ? 'null' : typeof item;
        (types[key] ??= new Set()).add(type);
        for (const text of flattenStrings(item)) {
          for (const match of text.matchAll(/<([A-Z0-9-]+)>/g)) placeholders.add(match[1]);
        }
      }
    }
    fieldKeys = [...fields].sort();
    fieldTypes = Object.fromEntries(Object.entries(types).sort().map(([key, set]) => [key, [...set].sort()]));
    placeholderTokens = [...placeholders].sort();
  }
  const displayCounts = {};
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    for (const record of Object.values(value)) {
      if (record && typeof record === 'object' && typeof record.name === 'string') {
        displayCounts[record.name] = (displayCounts[record.name] || 0) + 1;
      }
    }
  }
  result.tables.push({
    name,
    kind,
    count,
    keys,
    fieldKeys,
    fieldTypes,
    placeholderTokens,
    duplicateDisplayNames: Object.entries(displayCounts)
      .filter(([, duplicateCount]) => duplicateCount > 1)
      .map(([displayName, duplicateCount]) => ({ displayName, count: duplicateCount })),
  });
}
result.totalStructuredRecords = result.tables.reduce((total, table) => total + (table.count || 0), 0);
const rendered = `${JSON.stringify(result, null, 2)}\n`;
if (outputPath) fs.writeFileSync(outputPath, rendered);
else process.stdout.write(rendered);
