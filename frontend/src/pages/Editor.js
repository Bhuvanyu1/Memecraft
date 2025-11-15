import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { memeAPI, uploadAPI, trendAPI } from '@/services/api';
import { MemeCanvasEditor } from '@/lib/CanvasEditor';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Card } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { toast } from 'sonner';
import {
  Type,
  Image as ImageIcon,
  Trash2,
  Undo,
  Redo,
  Download,
  Save,
  ArrowLeft,
  Upload,
  Layers,
} from 'lucide-react';

const Editor = () => {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const canvasRef = useRef(null);
  const [editor, setEditor] = useState(null);
  const [activeObject, setActiveObject] = useState(null);
  const [memeTitle, setMemeTitle] = useState('Untitled Meme');
  const [saving, setSaving] = useState(false);

  // Text controls
  const [fontSize, setFontSize] = useState(48);
  const [textColor, setTextColor] = useState('#ffffff');
  const [strokeColor, setStrokeColor] = useState('#000000');
  const [fontFamily, setFontFamily] = useState('Impact');

  useEffect(() => {
    if (canvasRef.current) {
      const canvasEditor = new MemeCanvasEditor(canvasRef.current);
      setEditor(canvasEditor);

      // Load trend template if trendId provided
      const trendId = searchParams.get('trendId');
      if (trendId) {
        loadTrendTemplate(trendId, canvasEditor);
      }

      // Load existing meme if id provided
      if (id && id !== 'new') {
        loadMeme(id, canvasEditor);
      }

      // Listen for selection changes
      canvasEditor.canvas.on('selection:created', (e) => {
        setActiveObject(e.selected[0]);
      });
      canvasEditor.canvas.on('selection:updated', (e) => {
        setActiveObject(e.selected[0]);
      });
      canvasEditor.canvas.on('selection:cleared', () => {
        setActiveObject(null);
      });

      return () => {
        canvasEditor.dispose();
      };
    }
  }, [id, searchParams]);

  const loadTrendTemplate = async (trendId, canvasEditor) => {
    try {
      const response = await trendAPI.get(trendId);
      const trend = response.data;
      await canvasEditor.addImage(trend.image_url);
      setMemeTitle(trend.title);
      toast.success('Template loaded!');
    } catch (error) {
      console.error('Failed to load trend:', error);
      toast.error('Failed to load template');
    }
  };

  const loadMeme = async (memeId, canvasEditor) => {
    try {
      const response = await memeAPI.get(memeId);
      const meme = response.data;
      canvasEditor.loadFromJSON(meme.canvas_data);
      setMemeTitle(meme.title);
    } catch (error) {
      console.error('Failed to load meme:', error);
      toast.error('Failed to load meme');
    }
  };

  const handleAddText = () => {
    if (editor) {
      editor.addText('Edit Me', {
        fontSize,
        fill: textColor,
        stroke: strokeColor,
        fontFamily,
      });
    }
  };

  const handleImageUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file || !editor) return;

    try {
      toast.loading('Uploading image...');
      const response = await uploadAPI.image(file);
      const imageUrl = process.env.REACT_APP_BACKEND_URL + response.data.url;
      await editor.addImage(imageUrl);
      toast.success('Image added!');
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Failed to upload image');
    }
  };

  const handleUpdateText = () => {
    if (editor && activeObject && activeObject.type === 'i-text') {
      editor.updateActiveText({
        fontSize,
        fill: textColor,
        stroke: strokeColor,
        fontFamily,
      });
    }
  };

  const handleSave = async () => {
    if (!editor) return;

    setSaving(true);
    try {
      const canvasData = editor.toJSON();
      const thumbnailUrl = editor.exportToPNG(0.5);

      if (id && id !== 'new') {
        await memeAPI.update(id, {
          title: memeTitle,
          canvas_data: canvasData,
          thumbnail_url: thumbnailUrl,
        });
        toast.success('Meme saved!');
      } else {
        const response = await memeAPI.create({
          title: memeTitle,
          canvas_data: canvasData,
          thumbnail_url: thumbnailUrl,
          tags: [],
        });
        toast.success('Meme created!');
        navigate(`/editor/${response.data.id}`);
      }
    } catch (error) {
      console.error('Save error:', error);
      toast.error('Failed to save meme');
    }
    setSaving(false);
  };

  const handleExport = () => {
    if (!editor) return;

    const dataUrl = editor.exportToPNG();
    const link = document.createElement('a');
    link.download = `${memeTitle.replace(/\s+/g, '_')}.png`;
    link.href = dataUrl;
    link.click();
    toast.success('Meme exported!');
  };

  // Get all canvas objects for layers panel
  const [canvasObjects, setCanvasObjects] = useState([]);

  useEffect(() => {
    if (editor?.canvas) {
      const updateLayers = () => {
        setCanvasObjects([...editor.canvas.getObjects()]);
      };
      
      editor.canvas.on('object:added', updateLayers);
      editor.canvas.on('object:removed', updateLayers);
      editor.canvas.on('object:modified', updateLayers);
      
      return () => {
        editor.canvas.off('object:added', updateLayers);
        editor.canvas.off('object:removed', updateLayers);
        editor.canvas.off('object:modified', updateLayers);
      };
    }
  }, [editor]);

  const selectLayer = (obj) => {
    if (editor?.canvas) {
      editor.canvas.setActiveObject(obj);
      editor.canvas.renderAll();
      setActiveObject(obj);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-bg-darker" data-testid="editor-page">
      {/* Top Bar */}
      <header className="border-b border-slate-800 bg-bg-card/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/dashboard')}
              className="hover:bg-bg-hover"
              data-testid="back-button"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>

            <Input
              value={memeTitle}
              onChange={(e) => setMemeTitle(e.target.value)}
              className="w-64 bg-bg-darker border-slate-700 text-text-primary"
              placeholder="Meme title"
              data-testid="meme-title-input"
            />
          </div>

          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => editor?.undo()}
              disabled={!editor?.canUndo()}
              className="hover:bg-bg-hover border-slate-700"
              data-testid="undo-button"
            >
              <Undo className="h-4 w-4" />
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={() => editor?.redo()}
              disabled={!editor?.canRedo()}
              className="hover:bg-bg-hover border-slate-700"
              data-testid="redo-button"
            >
              <Redo className="h-4 w-4" />
            </Button>

            <Separator orientation="vertical" className="h-6" />

            <Button
              variant="outline"
              size="sm"
              onClick={handleExport}
              className="hover:bg-bg-hover border-slate-700"
              data-testid="export-button"
            >
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>

            <Button
              size="sm"
              onClick={handleSave}
              disabled={saving}
              className="bg-primary-green text-gray-900 hover:opacity-90"
              data-testid="save-button"
            >
              <Save className="h-4 w-4 mr-2" />
              {saving ? 'Saving...' : 'Save'}
            </Button>
          </div>
        </div>
      </header>

      {/* Main Editor - Three Column Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar - Tools */}
        <aside className="w-64 border-r border-slate-800 bg-bg-card/50 p-4 overflow-y-auto" data-testid="tools-sidebar">
          <div className="space-y-6">
            {/* Add Tools */}
            <div>
              <h3 className="text-sm font-semibold text-text-primary mb-3">Add Elements</h3>
              <div className="space-y-2">
                <Button
                  variant="outline"
                  className="w-full justify-start hover:bg-bg-hover hover:border-primary-green border-slate-700 text-text-primary"
                  onClick={handleAddText}
                  data-testid="add-text-button"
                >
                  <Type className="h-4 w-4 mr-2" />
                  Add Text
                </Button>

                <label className="w-full">
                  <Button
                    variant="outline"
                    className="w-full justify-start hover:bg-bg-hover hover:border-primary-blue border-slate-700 text-text-primary"
                    asChild
                    data-testid="add-image-button"
                  >
                    <span>
                      <ImageIcon className="h-4 w-4 mr-2" />
                      Add Image
                    </span>
                  </Button>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="hidden"
                  />
                </label>
              </div>
            </div>

            <Separator className="bg-slate-700" />

            {/* Text Controls */}
            {activeObject?.type === 'i-text' && (
              <div>
                <h3 className="text-sm font-semibold text-text-primary mb-3">Text Style</h3>
                <div className="space-y-4">
                  <div>
                    <Label className="text-xs text-text-secondary">Font Family</Label>
                    <select
                      value={fontFamily}
                      onChange={(e) => {
                        setFontFamily(e.target.value);
                        handleUpdateText();
                      }}
                      className="w-full mt-1 bg-bg-darker border border-slate-700 rounded px-2 py-1 text-sm text-text-primary"
                      data-testid="font-family-select"
                    >
                      <option value="Impact">Impact</option>
                      <option value="Arial">Arial</option>
                      <option value="Comic Sans MS">Comic Sans</option>
                      <option value="Times New Roman">Times New Roman</option>
                    </select>
                  </div>

                  <div>
                    <Label className="text-xs text-text-secondary">Font Size: {fontSize}</Label>
                    <Slider
                      value={[fontSize]}
                      onValueChange={([val]) => {
                        setFontSize(val);
                        handleUpdateText();
                      }}
                      min={12}
                      max={120}
                      step={1}
                      className="mt-2"
                      data-testid="font-size-slider"
                    />
                  </div>

                  <div>
                    <Label className="text-xs text-text-secondary">Text Color</Label>
                    <input
                      type="color"
                      value={textColor}
                      onChange={(e) => {
                        setTextColor(e.target.value);
                        handleUpdateText();
                      }}
                      className="w-full h-10 rounded mt-1"
                      data-testid="text-color-input"
                    />
                  </div>

                  <div>
                    <Label className="text-xs text-text-secondary">Stroke Color</Label>
                    <input
                      type="color"
                      value={strokeColor}
                      onChange={(e) => {
                        setStrokeColor(e.target.value);
                        handleUpdateText();
                      }}
                      className="w-full h-10 rounded mt-1"
                      data-testid="stroke-color-input"
                    />
                  </div>
                </div>
              </div>
            )}

            <Separator className="bg-slate-700" />

            {/* Actions */}
            <div>
              <h3 className="text-sm font-semibold text-text-primary mb-3">Actions</h3>
              <div className="space-y-2">
                <Button
                  variant="outline"
                  className="w-full justify-start hover:bg-bg-hover border-slate-700 text-text-primary"
                  onClick={() => editor?.bringToFront()}
                  disabled={!activeObject}
                  data-testid="bring-front-button"
                >
                  <Layers className="h-4 w-4 mr-2" />
                  Bring to Front
                </Button>

                <Button
                  variant="outline"
                  className="w-full justify-start hover:bg-bg-hover border-slate-700 text-text-primary"
                  onClick={() => editor?.sendToBack()}
                  disabled={!activeObject}
                  data-testid="send-back-button"
                >
                  <Layers className="h-4 w-4 mr-2" />
                  Send to Back
                </Button>

                <Button
                  variant="outline"
                  className="w-full justify-start hover:bg-accent-error hover:border-accent-error border-slate-700 text-accent-error"
                  onClick={() => editor?.deleteActiveLayer()}
                  disabled={!activeObject}
                  data-testid="delete-layer-button"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </Button>
              </div>
            </div>
          </div>
        </aside>

        {/* Center - Canvas Area */}
        <div className="flex-1 flex items-center justify-center bg-bg-dark p-8" data-testid="canvas-container">
          <div className="bg-white shadow-2xl rounded-lg overflow-hidden">
            <canvas ref={canvasRef} data-testid="meme-canvas" />
          </div>
        </div>

        {/* Right Sidebar - Layers */}
        <aside className="w-64 border-l border-slate-800 bg-bg-card/50 p-4 overflow-y-auto" data-testid="layers-sidebar">
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-semibold text-text-primary mb-3 flex items-center">
                <Layers className="h-4 w-4 mr-2 text-primary-purple" />
                Layers
              </h3>
              
              {canvasObjects.length === 0 ? (
                <p className="text-xs text-text-muted text-center py-8">
                  No layers yet.<br />Add text or images to get started.
                </p>
              ) : (
                <div className="space-y-2">
                  {canvasObjects.map((obj, index) => (
                    <div
                      key={index}
                      onClick={() => selectLayer(obj)}
                      className={`p-3 rounded-lg cursor-pointer transition-all duration-200 border ${
                        activeObject === obj
                          ? 'bg-bg-hover border-primary-purple'
                          : 'bg-bg-darker border-slate-700 hover:border-slate-600 hover:bg-bg-hover'
                      }`}
                      data-testid={`layer-item-${index}`}
                    >
                      <div className="flex items-center space-x-2">
                        {obj.type === 'i-text' ? (
                          <Type className="h-4 w-4 text-primary-green" />
                        ) : (
                          <ImageIcon className="h-4 w-4 text-primary-blue" />
                        )}
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-text-primary truncate">
                            {obj.type === 'i-text' ? obj.text || 'Text Layer' : 'Image Layer'}
                          </p>
                          <p className="text-xs text-text-muted">
                            {obj.type === 'i-text' ? 'Text' : 'Image'}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
};

export default Editor;
