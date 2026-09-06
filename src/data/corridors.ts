/**
 * Official Corridor tile pool for Nemesis: Retaliation (40 corridor tiles).
 * 10 each of values 1, 2, 3, 4.
 */

export interface CorridorTileDefinition {
  readonly id: string;
  readonly number: number;
  readonly noiseValue: number;
  readonly deadlyNoiseValue?: number;
  readonly hasDoor: boolean;
}

export const CORRIDOR_TILES: readonly CorridorTileDefinition[] = [
  {
    id: "corridor-tile-101",
    number: 101,
    noiseValue: 1,
    hasDoor: true,
  },
  {
    id: "corridor-tile-102",
    number: 102,
    noiseValue: 1,
    hasDoor: true,
  },
  {
    id: "corridor-tile-103",
    number: 103,
    noiseValue: 1,
    hasDoor: true,
  },
  {
    id: "corridor-tile-104",
    number: 104,
    noiseValue: 1,
    hasDoor: false,
  },
  {
    id: "corridor-tile-105",
    number: 105,
    noiseValue: 1,
    hasDoor: false,
  },
  {
    id: "corridor-tile-106",
    number: 106,
    noiseValue: 1,
    hasDoor: false,
  },
  {
    id: "corridor-tile-107",
    number: 107,
    noiseValue: 1,
    deadlyNoiseValue: 2,
    hasDoor: false,
  },
  {
    id: "corridor-tile-108",
    number: 108,
    noiseValue: 1,
    deadlyNoiseValue: 2,
    hasDoor: false,
  },
  {
    id: "corridor-tile-109",
    number: 109,
    noiseValue: 1,
    deadlyNoiseValue: 3,
    hasDoor: false,
  },
  {
    id: "corridor-tile-110",
    number: 110,
    noiseValue: 1,
    deadlyNoiseValue: 4,
    hasDoor: false,
  },
  {
    id: "corridor-tile-111",
    number: 111,
    noiseValue: 1,
    hasDoor: true,
  },
  {
    id: "corridor-tile-201",
    number: 201,
    noiseValue: 2,
    hasDoor: true,
  },
  {
    id: "corridor-tile-202",
    number: 202,
    noiseValue: 2,
    hasDoor: true,
  },
  {
    id: "corridor-tile-203",
    number: 203,
    noiseValue: 2,
    hasDoor: true,
  },
  {
    id: "corridor-tile-204",
    number: 204,
    noiseValue: 2,
    hasDoor: false,
  },
  {
    id: "corridor-tile-205",
    number: 205,
    noiseValue: 2,
    hasDoor: false,
  },
  {
    id: "corridor-tile-206",
    number: 206,
    noiseValue: 2,
    hasDoor: false,
  },
  {
    id: "corridor-tile-207",
    number: 207,
    noiseValue: 2,
    deadlyNoiseValue: 1,
    hasDoor: false,
  },
  {
    id: "corridor-tile-208",
    number: 208,
    noiseValue: 2,
    deadlyNoiseValue: 1,
    hasDoor: false,
  },
  {
    id: "corridor-tile-209",
    number: 209,
    noiseValue: 2,
    deadlyNoiseValue: 3,
    hasDoor: false,
  },
  {
    id: "corridor-tile-210",
    number: 210,
    noiseValue: 2,
    deadlyNoiseValue: 4,
    hasDoor: false,
  },
  {
    id: "corridor-tile-211",
    number: 211,
    noiseValue: 2,
    hasDoor: true,
  },
  {
    id: "corridor-tile-301",
    number: 301,
    noiseValue: 3,
    hasDoor: true,
  },
  {
    id: "corridor-tile-302",
    number: 302,
    noiseValue: 3,
    hasDoor: true,
  },
  {
    id: "corridor-tile-303",
    number: 303,
    noiseValue: 3,
    hasDoor: true,
  },
  {
    id: "corridor-tile-304",
    number: 304,
    noiseValue: 3,
    hasDoor: false,
  },
  {
    id: "corridor-tile-305",
    number: 305,
    noiseValue: 3,
    hasDoor: false,
  },
  {
    id: "corridor-tile-306",
    number: 306,
    noiseValue: 3,
    hasDoor: false,
  },
  {
    id: "corridor-tile-307",
    number: 307,
    noiseValue: 3,
    deadlyNoiseValue: 4,
    hasDoor: false,
  },
  {
    id: "corridor-tile-308",
    number: 308,
    noiseValue: 3,
    deadlyNoiseValue: 1,
    hasDoor: false,
  },
  {
    id: "corridor-tile-309",
    number: 309,
    noiseValue: 3,
    deadlyNoiseValue: 2,
    hasDoor: false,
  },
  {
    id: "corridor-tile-310",
    number: 310,
    noiseValue: 3,
    deadlyNoiseValue: 4,
    hasDoor: false,
  },
  {
    id: "corridor-tile-311",
    number: 311,
    noiseValue: 3,
    hasDoor: true,
  },
  {
    id: "corridor-tile-401",
    number: 401,
    noiseValue: 4,
    hasDoor: true,
  },
  {
    id: "corridor-tile-402",
    number: 402,
    noiseValue: 4,
    hasDoor: true,
  },
  {
    id: "corridor-tile-403",
    number: 403,
    noiseValue: 4,
    hasDoor: true,
  },
  {
    id: "corridor-tile-404",
    number: 404,
    noiseValue: 4,
    hasDoor: false,
  },
  {
    id: "corridor-tile-405",
    number: 405,
    noiseValue: 4,
    hasDoor: false,
  },
  {
    id: "corridor-tile-406",
    number: 406,
    noiseValue: 4,
    hasDoor: false,
  },
  {
    id: "corridor-tile-407",
    number: 407,
    noiseValue: 4,
    deadlyNoiseValue: 3,
    hasDoor: false,
  },
  {
    id: "corridor-tile-408",
    number: 408,
    noiseValue: 4,
    deadlyNoiseValue: 1,
    hasDoor: false,
  },
  {
    id: "corridor-tile-409",
    number: 409,
    noiseValue: 4,
    deadlyNoiseValue: 2,
    hasDoor: false,
  },
  {
    id: "corridor-tile-410",
    number: 410,
    noiseValue: 4,
    deadlyNoiseValue: 3,
    hasDoor: false,
  },
  {
    id: "corridor-tile-411",
    number: 411,
    noiseValue: 4,
    hasDoor: true,
  },
] as const;
