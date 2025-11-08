import { fabric } from 'fabric';

export class MemeCanvasEditor {
  constructor(canvasElement, options = {}) {
    this.canvas = new fabric.Canvas(canvasElement, {
      width: options.width || 1200,
      height: options.height || 675,
      backgroundColor: options.backgroundColor || '#ffffff',
    });

    this.history = [];
    this.historyStep = -1;
    this.setupEventListeners();
  }

  setupEventListeners() {
    this.canvas.on('object:added', () => this.saveState());
    this.canvas.on('object:modified', () => this.saveState());
    this.canvas.on('object:removed', () => this.saveState());
  }

  // Text Operations
  addText(text = 'Edit Me', options = {}) {
    const textObject = new fabric.IText(text, {
      left: 100,
      top: 100,
      fontFamily: options.fontFamily || 'Impact',
      fontSize: options.fontSize || 48,
      fill: options.fill || '#ffffff',
      stroke: options.stroke || '#000000',
      strokeWidth: options.strokeWidth || 2,
      textAlign: 'center',
      ...options,
    });

    this.canvas.add(textObject);
    this.canvas.setActiveObject(textObject);
    this.canvas.renderAll();
    return textObject;
  }

  updateActiveText(properties) {
    const activeObject = this.canvas.getActiveObject();
    if (activeObject && activeObject.type === 'i-text') {
      activeObject.set(properties);
      this.canvas.renderAll();
    }
  }

  // Image Operations
  async addImage(imageUrl) {
    return new Promise((resolve, reject) => {
      fabric.Image.fromURL(
        imageUrl,
        (img) => {
          if (!img) {
            reject(new Error('Failed to load image'));
            return;
          }

          const maxWidth = this.canvas.width * 0.8;
          const maxHeight = this.canvas.height * 0.8;
          const scale = Math.min(maxWidth / img.width, maxHeight / img.height);

          img.scale(scale);
          img.set({
            left: (this.canvas.width - img.width * scale) / 2,
            top: (this.canvas.height - img.height * scale) / 2,
          });

          this.canvas.add(img);
          this.canvas.setActiveObject(img);
          this.canvas.renderAll();
          resolve(img);
        },
        { crossOrigin: 'anonymous' }
      );
    });
  }

  // Layer Operations
  getLayers() {
    return this.canvas.getObjects();
  }

  deleteActiveLayer() {
    const activeObject = this.canvas.getActiveObject();
    if (activeObject) {
      this.canvas.remove(activeObject);
      this.canvas.renderAll();
    }
  }

  bringToFront() {
    const activeObject = this.canvas.getActiveObject();
    if (activeObject) {
      this.canvas.bringToFront(activeObject);
      this.canvas.renderAll();
    }
  }

  sendToBack() {
    const activeObject = this.canvas.getActiveObject();
    if (activeObject) {
      this.canvas.sendToBack(activeObject);
      this.canvas.renderAll();
    }
  }

  // History Management
  saveState() {
    const json = JSON.stringify(this.canvas.toJSON());
    
    if (this.historyStep < this.history.length - 1) {
      this.history = this.history.slice(0, this.historyStep + 1);
    }
    
    this.history.push(json);
    this.historyStep = this.history.length - 1;

    if (this.history.length > 50) {
      this.history.shift();
      this.historyStep--;
    }
  }

  undo() {
    if (this.historyStep > 0) {
      this.historyStep--;
      this.loadFromJSON(this.history[this.historyStep]);
    }
  }

  redo() {
    if (this.historyStep < this.history.length - 1) {
      this.historyStep++;
      this.loadFromJSON(this.history[this.historyStep]);
    }
  }

  canUndo() {
    return this.historyStep > 0;
  }

  canRedo() {
    return this.historyStep < this.history.length - 1;
  }

  // Export Operations
  exportToPNG(quality = 1) {
    return this.canvas.toDataURL({
      format: 'png',
      quality: quality,
    });
  }

  exportToJPEG(quality = 0.9) {
    return this.canvas.toDataURL({
      format: 'jpeg',
      quality: quality,
    });
  }

  // Canvas Operations
  clear() {
    this.canvas.clear();
    this.canvas.backgroundColor = '#ffffff';
    this.canvas.renderAll();
  }

  setBackground(color) {
    this.canvas.backgroundColor = color;
    this.canvas.renderAll();
  }

  setSize(width, height) {
    this.canvas.setWidth(width);
    this.canvas.setHeight(height);
    this.canvas.renderAll();
  }

  // Serialization
  toJSON() {
    return this.canvas.toJSON();
  }

  loadFromJSON(json) {
    const data = typeof json === 'string' ? JSON.parse(json) : json;
    this.canvas.loadFromJSON(data, () => {
      this.canvas.renderAll();
    });
  }

  getActiveObject() {
    return this.canvas.getActiveObject();
  }

  dispose() {
    this.canvas.dispose();
  }
}
