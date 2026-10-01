/** RGB color, each channel 0-255. */
export type Color = [number, number, number];
/** Three-tone palette: shadow, mid, highlight. */
export type Palette3 = [Color, Color, Color];
/** RGBA color, each channel 0-255. */
export type RGBA = [number, number, number, number];
/**
 * Row-major RGBA pixel buffer.
 * Stride = width * 4. Pixel (x, y) starts at offset (y * width + x) * 4.
 */
export declare class Canvas {
    readonly width: number;
    readonly height: number;
    readonly data: Uint8ClampedArray;
    constructor(width: number, height: number, data?: Uint8ClampedArray);
    getPixel(x: number, y: number): RGBA;
    setPixel(x: number, y: number, r: number, g: number, b: number, a: number): void;
}
