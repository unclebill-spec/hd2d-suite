/** Shared composition utilities for sprite generators. */
import { type EllipseSpec } from './primitives.js';
import { Rng } from './rng.js';
import { Canvas, type Color, type Palette3, type RGBA } from './types.js';
export type Point = {
    x: number;
    y: number;
};
/** Pick N unique indices from [0, length) via partial Fisher-Yates shuffle. */
export declare function sampleUniqueIndices(rng: Rng, length: number, count: number): number[];
export declare function pick<T>(rng: Rng, items: readonly T[]): T;
export declare function jitterColor(rng: Rng, base: Color, delta: number, min?: Color, max?: Color): Color;
export declare function shiftColor(base: Color, dr: number, dg: number, db: number): Color;
export declare function asRgba(color: Color, alpha: number): RGBA;
export declare function lightenRgba(rgba: RGBA, amount: number): RGBA;
/**
 * Distribute lobe centers in a ring around (cx, cy).
 *
 * verticalBias: [belowScale, aboveScale] compresses vertical
 * distance for lobes below/above center (canvas Y-down).
 */
export declare function distributeLobes(rng: Rng, cx: number, cy: number, count: number, radius: number, distRange: [number, number], angleJitter?: number, verticalBias?: [number, number]): Point[];
/**
 * Stamp shadow / body / highlight ellipse layers using a Palette3.
 * Default parameters are tuned for stone surfaces.
 */
export declare function stampThreeTone(canvas: Canvas, pal: Palette3, shadowEllipses: EllipseSpec[], bodyEllipses: EllipseSpec[], highlightEllipses: EllipseSpec[], falloff?: [number, number, number], hardness?: [number, number, number], alpha?: [number, number, number]): void;
