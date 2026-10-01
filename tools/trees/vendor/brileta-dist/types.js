/**
 * Row-major RGBA pixel buffer.
 * Stride = width * 4. Pixel (x, y) starts at offset (y * width + x) * 4.
 */
export class Canvas {
    constructor(width, height, data) {
        this.width = width;
        this.height = height;
        this.data = data ?? new Uint8ClampedArray(width * height * 4);
    }
    getPixel(x, y) {
        const i = (y * this.width + x) * 4;
        return [this.data[i], this.data[i + 1], this.data[i + 2], this.data[i + 3]];
    }
    setPixel(x, y, r, g, b, a) {
        const i = (y * this.width + x) * 4;
        this.data[i] = r;
        this.data[i + 1] = g;
        this.data[i + 2] = b;
        this.data[i + 3] = a;
    }
}
//# sourceMappingURL=types.js.map