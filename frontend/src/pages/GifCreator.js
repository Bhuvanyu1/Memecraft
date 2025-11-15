import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { MemeCanvasEditor } from '@/lib/CanvasEditor';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import { toast } from 'sonner';
import GIF from 'gif.js';
import {
  ArrowLeft,
  Play,
  Pause,
  Plus,
  Trash2,
  Copy,
  Download,
  Loader2,
} from 'lucide-react';

const GifCreator = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const canvasRef = useRef(null);
  const [editor, setEditor] = useState(null);
  const [frames, setFrames] = useState([]);
  const [currentFrameIndex, setCurrentFrameIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [gifTitle, setGifTitle] = useState('My Animated Meme');
  const [exporting, setExporting] = useState(false);
  const playIntervalRef = useRef(null);

  useEffect(() => {
    if (canvasRef.current) {
      const canvasEditor = new MemeCanvasEditor(canvasRef.current, {
        width: 800,
        height: 600,
      });
      setEditor(canvasEditor);

      // Add initial frame
      const initialFrame = {
        id: Date.now(),
        canvasData: canvasEditor.toJSON(),
        duration: 1000,
        thumbnail: canvasEditor.exportToPNG(0.3),
      };
      setFrames([initialFrame]);

      return () => {
        canvasEditor.dispose();
      };
    }
  }, []);

  const captureCurrentFrame = () => {
    if (!editor) return null;
    return {
      id: Date.now(),
      canvasData: editor.toJSON(),
      duration: 1000,
      thumbnail: editor.exportToPNG(0.3),
    };
  };

  const handleAddFrame = () => {
    const newFrame = captureCurrentFrame();
    if (newFrame) {
      setFrames([...frames, newFrame]);
      setCurrentFrameIndex(frames.length);
      toast.success('Frame added');
    }
  };

  const handleDuplicateFrame = (index) => {
    const frameToDuplicate = frames[index];
    const duplicatedFrame = {
      ...frameToDuplicate,
      id: Date.now(),
    };
    const newFrames = [...frames];
    newFrames.splice(index + 1, 0, duplicatedFrame);
    setFrames(newFrames);
    toast.success('Frame duplicated');
  };

  const handleDeleteFrame = (index) => {
    if (frames.length <= 1) {
      toast.error('Cannot delete the only frame');
      return;
    }
    const newFrames = frames.filter((_, i) => i !== index);
    setFrames(newFrames);
    if (currentFrameIndex >= newFrames.length) {
      setCurrentFrameIndex(newFrames.length - 1);
      loadFrame(newFrames.length - 1);
    }
    toast.success('Frame deleted');
  };

  const loadFrame = (index) => {
    if (!editor || !frames[index]) return;
    editor.loadFromJSON(frames[index].canvasData);
    setCurrentFrameIndex(index);
  };

  const updateFrameDuration = (index, duration) => {
    const newFrames = [...frames];
    newFrames[index].duration = duration;
    setFrames(newFrames);
  };

  const handlePlay = () => {
    if (frames.length === 0) return;
    
    setIsPlaying(true);
    let index = 0;

    const playFrame = () => {
      loadFrame(index);
      playIntervalRef.current = setTimeout(() => {
        index = (index + 1) % frames.length;
        playFrame();
      }, frames[index].duration);
    };

    playFrame();
  };

  const handleStop = () => {
    setIsPlaying(false);
    if (playIntervalRef.current) {
      clearTimeout(playIntervalRef.current);
      playIntervalRef.current = null;
    }
  };

  const handleExportGIF = async () => {
    if (frames.length === 0) {
      toast.error('No frames to export');
      return;
    }

    setExporting(true);
    toast.loading('Generating GIF... This may take a moment');

    try {
      const gif = new GIF({
        workers: 2,
        quality: 10,
        width: 800,
        height: 600,
        workerScript: 'https://cdn.jsdelivr.net/npm/gif.js@0.2.0/dist/gif.worker.js',
      });

      // Add each frame to GIF
      for (const frame of frames) {
        // Create a temporary canvas for this frame
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = 800;
        tempCanvas.height = 600;
        const tempEditor = new MemeCanvasEditor(tempCanvas);
        tempEditor.loadFromJSON(frame.canvasData);
        
        await new Promise(resolve => setTimeout(resolve, 100)); // Wait for render
        
        gif.addFrame(tempCanvas, { delay: frame.duration });
        tempEditor.dispose();
      }

      gif.on('finished', (blob) => {
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.download = `${gifTitle.replace(/\s+/g, '_')}.gif`;
        link.href = url;
        link.click();
        
        toast.success('GIF exported successfully!');
        setExporting(false);
      });

      gif.render();
    } catch (error) {
      console.error('GIF export error:', error);
      toast.error('Failed to export GIF');
      setExporting(false);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-bg-darker" data-testid="gif-creator-page">
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
              value={gifTitle}
              onChange={(e) => setGifTitle(e.target.value)}
              className="w-64 bg-bg-darker border-slate-700 text-text-primary"
              placeholder="GIF title"
              data-testid="gif-title-input"
            />
          </div>

          <div className="flex items-center space-x-2">
            {isPlaying ? (
              <Button
                variant="outline"
                size="sm"
                onClick={handleStop}
                className="hover:bg-bg-hover border-slate-700"
                data-testid="stop-button"
              >
                <Pause className="h-4 w-4 mr-2" />
                Stop
              </Button>
            ) : (
              <Button
                variant="outline"
                size="sm"
                onClick={handlePlay}
                disabled={frames.length === 0}
                className="hover:bg-bg-hover hover:border-primary-purple border-slate-700"
                data-testid="play-button"
              >
                <Play className="h-4 w-4 mr-2" />
                Preview
              </Button>
            )}

            <Button
              size="sm"
              onClick={handleExportGIF}
              disabled={exporting || frames.length === 0}
              className="bg-primary-green text-gray-900 hover:opacity-90"
              data-testid="export-gif-button"
            >
              {exporting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Exporting...
                </>
              ) : (
                <>
                  <Download className="h-4 w-4 mr-2" />
                  Export GIF
                </>
              )}
            </Button>
          </div>
        </div>
      </header>

      {/* Main Editor */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Canvas Area */}
        <div className="flex-1 flex items-center justify-center bg-bg-dark p-8" data-testid="canvas-container">
          <div className="bg-white shadow-2xl rounded-lg overflow-hidden">
            <canvas ref={canvasRef} data-testid="gif-canvas" />
          </div>
        </div>

        {/* Timeline */}
        <div className="border-t border-slate-800 bg-bg-card/50 p-4" data-testid="timeline-container">
          <div className="container mx-auto">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-4">
                <h3 className="text-text-primary font-semibold">Timeline</h3>
                <span className="text-sm text-text-secondary">
                  Frame {currentFrameIndex + 1} of {frames.length}
                </span>
              </div>

              <Button
                onClick={handleAddFrame}
                size="sm"
                className="bg-primary-blue text-white hover:opacity-90"
                data-testid="add-frame-button"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Frame
              </Button>
            </div>

            {/* Timeline Frames */}
            <div className="flex space-x-2 overflow-x-auto pb-2">
              {frames.map((frame, index) => (
                <Card
                  key={frame.id}
                  className={`flex-shrink-0 cursor-pointer transition-all rounded-xl ${
                    index === currentFrameIndex
                      ? 'border-primary-green border-2 bg-bg-card'
                      : 'border-slate-700 bg-bg-darker hover:border-slate-600'
                  }`}
                  onClick={() => loadFrame(index)}
                  data-testid={`frame-${index}`}
                >
                  <CardContent className="p-2">
                    <div className="w-32 h-24 bg-bg-dark rounded overflow-hidden mb-2">
                      <img
                        src={frame.thumbnail}
                        alt={`Frame ${index + 1}`}
                        className="w-full h-full object-cover"
                      />
                    </div>

                    <div className="space-y-2">
                      <div className="text-xs text-text-primary text-center">
                        Frame {index + 1}
                      </div>

                      <div className="space-y-1">
                        <Label className="text-xs text-text-secondary">
                          Duration: {frame.duration}ms
                        </Label>
                        <Slider
                          value={[frame.duration]}
                          onValueChange={([val]) => updateFrameDuration(index, val)}
                          min={100}
                          max={3000}
                          step={100}
                          className="w-full"
                          data-testid={`duration-slider-${index}`}
                        />
                      </div>

                      <div className="flex space-x-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDuplicateFrame(index);
                          }}
                          className="flex-1 h-7 text-xs hover:bg-bg-hover"
                          data-testid={`duplicate-frame-${index}`}
                        >
                          <Copy className="h-3 w-3" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteFrame(index);
                          }}
                          className="flex-1 h-7 text-xs text-accent-error hover:bg-accent-error/10"
                          disabled={frames.length <= 1}
                          data-testid={`delete-frame-${index}`}
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GifCreator;
