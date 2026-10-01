/** Sprite drawing primitives. */
import { Canvas } from './types.js';
import { Rng } from './rng.js';
export declare function clamp(v: number, lo: number, hi: number): number;
export declare function clampChannel(v: number): number;
/**
 * Compute rim mask: pixels with alpha > 128 that have a cardinal neighbor
 * at alpha == 0 (or canvas border).
 */
export declare function computeRimMask(canvas: Canvas): Uint8Array;
export interface EllipseSpec {
    cx: number;
    cy: number;
    rx: number;
    ry: number;
}
/**
 * Stamp a single ellipse with alpha-over blending.
 * Alpha is 0-255. Falloff and hardness control the edge profile.
 */
export declare function stampEllipse(canvas: Canvas, cx: number, cy: number, rx: number, ry: number, r: number, g: number, b: number, alpha: number, falloff: number, hardness: number): void;
/**
 * Batch stamp ellipses with screen-blend alpha accumulation.
 * Order-independent compositing: each ellipse contributes
 * remaining[px] *= (1 - alpha_i). Final alpha = 1 - remaining.
 */
export declare function batchStampEllipses(canvas: Canvas, ellipses: EllipseSpec[], r: number, g: number, b: number, alpha: number, falloff: number, hardness: number): void;
/**
 * Darken rim pixels by subtracting (dr, dg, db), clamped to 0.
 * Rim = alpha > 128 with a cardinal neighbor at alpha == 0.
 */
export declare function darkenRim(canvas: Canvas, dr: number, dg: number, db: number): void;
/**
 * For each masked pixel, compute the horizontal opaque span width.
 * Useful as a nibble guard to protect thin structural features.
 */
export declare function computeSpanWidths(canvas: Canvas, mask: Uint8Array): Uint8Array;
/**
 * Shift sprite content down so the last opaque row sits at the canvas bottom.
 * Useful for ground-anchored sprites (boulders, stumps, etc.).
 */
export declare function shiftToBottom(canvas: Canvas): void;
/**
 * Check whether removing the opaque pixel at (row, col) would disconnect
 * its opaque neighbors.  Examines the 8-neighbor ring (N, NE, E, SE, S,
 * SW, W, NW) and counts 4-connected components among the opaque entries.
 * If there are two or more components, the center pixel is a bridge and
 * erasing it would split the sprite.
 */
export declare function wouldDisconnect(data: Uint8ClampedArray, w: number, h: number, row: number, col: number): boolean;
export interface NibbleOpts {
    /** Called when the coin flip succeeds. Return true to allow erasure. */
    guard?: (row: number, col: number) => boolean;
    /** Called after a pixel is erased. */
    onErase?: (row: number, col: number) => void;
}
/**
 * Erase rim pixels where mask is set, with the given probability.
 * Consumes one RNG call per masked pixel (preserving determinism
 * regardless of guard outcome).
 */
export declare function nibbleRim(canvas: Canvas, rng: Rng, nibbleProb: number, mask: Uint8Array, opts?: NibbleOpts): void;
/**
 * Bresenham thick line. For each point on the line, stamps a filled
 * square of the given thickness centered on the point.
 */
export declare function drawLine(canvas: Canvas, x0: number, y0: number, x1: number, y1: number, r: number, g: number, b: number, a: number, thickness: number): void;
/**
 * Scanline triangle fill.
 */
export declare function fillTriangle(canvas: Canvas, x0: number, y0: number, x1: number, y1: number, x2: number, y2: number, r: number, g: number, b: number, a: number): void;
