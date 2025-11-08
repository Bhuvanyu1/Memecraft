import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { aiAPI } from '@/services/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import { ArrowLeft, Sparkles, Loader2, Wand2, Image as ImageIcon } from 'lucide-react';

const AIGenerator = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  
  // Meme Generator State
  const [memeTopic, setMemeTopic] = useState('');
  const [humorStyle, setHumorStyle] = useState('sarcastic');
  const [generatingMeme, setGeneratingMeme] = useState(false);
  const [generatedMeme, setGeneratedMeme] = useState(null);

  // Image Generator State
  const [imagePrompt, setImagePrompt] = useState('');
  const [generatingImage, setGeneratingImage] = useState(false);
  const [generatedImage, setGeneratedImage] = useState(null);

  const handleGenerateMeme = async () => {
    if (!memeTopic.trim()) {
      toast.error('Please enter a topic');
      return;
    }

    setGeneratingMeme(true);
    try {
      const response = await aiAPI.generateMeme({ topic: memeTopic, humor_style: humorStyle });
      setGeneratedMeme(response.data);
      toast.success('Meme generated!');
    } catch (error) {
      console.error('Meme generation error:', error);
      toast.error('Failed to generate meme');
    }
    setGeneratingMeme(false);
  };

  const handleGenerateImage = async () => {
    if (!imagePrompt.trim()) {
      toast.error('Please enter a prompt');
      return;
    }

    setGeneratingImage(true);
    try {
      const response = await aiAPI.generateImage({ prompt: imagePrompt });
      setGeneratedImage(response.data.image_url);
      toast.success('Image generated!');
    } catch (error) {
      console.error('Image generation error:', error);
      toast.error('Failed to generate image');
    }
    setGeneratingImage(false);
  };

  const handleUseInEditor = (imageUrl) => {
    // Store image URL in sessionStorage and navigate to editor
    sessionStorage.setItem('aiGeneratedImage', imageUrl);
    navigate('/editor/new');
  };

  return (
    <div className="min-h-screen bg-slate-950" data-testid="ai-generator-page">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/dashboard')}
              data-testid="back-button"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Dashboard
            </Button>

            <div>
              <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-blue-500">
                AI Meme Generator
              </h1>
              <p className="text-sm text-slate-400">Let AI create viral memes for you</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 max-w-4xl">
        <Tabs defaultValue="meme" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="meme" data-testid="tab-meme">
              <Sparkles className="h-4 w-4 mr-2" />
              Complete Meme
            </TabsTrigger>
            <TabsTrigger value="image" data-testid="tab-image">
              <ImageIcon className="h-4 w-4 mr-2" />
              Image Only
            </TabsTrigger>
          </TabsList>

          {/* Complete Meme Generator */}
          <TabsContent value="meme" className="space-y-6">
            <Card className="bg-slate-900/50 border-slate-800">
              <CardHeader>
                <CardTitle>Generate Complete Meme</CardTitle>
                <CardDescription>
                  Enter a topic and let AI create the perfect meme with text and image
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="memeTopic">Meme Topic</Label>
                  <Input
                    id="memeTopic"
                    placeholder="e.g., Monday mornings, Working from home, Coffee addiction"
                    value={memeTopic}
                    onChange={(e) => setMemeTopic(e.target.value)}
                    data-testid="meme-topic-input"
                  />
                </div>

                <div>
                  <Label htmlFor="humorStyle">Humor Style</Label>
                  <select
                    id="humorStyle"
                    value={humorStyle}
                    onChange={(e) => setHumorStyle(e.target.value)}
                    className="w-full mt-1 bg-slate-800 border border-slate-700 rounded-md px-3 py-2 text-white"
                    data-testid="humor-style-select"
                  >
                    <option value="sarcastic">Sarcastic</option>
                    <option value="wholesome">Wholesome</option>
                    <option value="dark">Dark Humor</option>
                    <option value="silly">Silly</option>
                    <option value="relatable">Relatable</option>
                  </select>
                </div>

                <Button
                  onClick={handleGenerateMeme}
                  disabled={generatingMeme}
                  className="w-full"
                  data-testid="generate-meme-button"
                >
                  {generatingMeme ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4 mr-2" />
                      Generate Meme
                    </>
                  )}
                </Button>

                {generatedMeme && (
                  <div className="mt-6 space-y-4" data-testid="generated-meme-result">
                    <div className="border border-slate-700 rounded-lg p-4 bg-slate-800">
                      <h3 className="font-semibold text-white mb-2">{generatedMeme.title}</h3>
                      {generatedMeme.top_text && (
                        <p className="text-sm text-slate-300 mb-1">
                          <strong>Top Text:</strong> {generatedMeme.top_text}
                        </p>
                      )}
                      {generatedMeme.bottom_text && (
                        <p className="text-sm text-slate-300 mb-3">
                          <strong>Bottom Text:</strong> {generatedMeme.bottom_text}
                        </p>
                      )}
                      {generatedMeme.image_url && (
                        <div className="rounded-lg overflow-hidden">
                          <img
                            src={generatedMeme.image_url}
                            alt="Generated meme"
                            className="w-full"
                          />
                        </div>
                      )}
                    </div>

                    {generatedMeme.image_url && (
                      <Button
                        onClick={() => handleUseInEditor(generatedMeme.image_url)}
                        className="w-full"
                        data-testid="use-in-editor-button"
                      >
                        <Wand2 className="h-4 w-4 mr-2" />
                        Open in Editor
                      </Button>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Image Generator */}
          <TabsContent value="image" className="space-y-6">
            <Card className="bg-slate-900/50 border-slate-800">
              <CardHeader>
                <CardTitle>Generate Image</CardTitle>
                <CardDescription>
                  Describe the image you want and AI will create it
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="imagePrompt">Image Description</Label>
                  <Textarea
                    id="imagePrompt"
                    placeholder="e.g., A cat wearing sunglasses sitting at a computer desk, digital art"
                    value={imagePrompt}
                    onChange={(e) => setImagePrompt(e.target.value)}
                    rows={4}
                    data-testid="image-prompt-input"
                  />
                  <p className="text-xs text-slate-400 mt-2">
                    Be specific! Include style, mood, and details for best results.
                  </p>
                </div>

                <Button
                  onClick={handleGenerateImage}
                  disabled={generatingImage}
                  className="w-full"
                  data-testid="generate-image-button"
                >
                  {generatingImage ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Generating... (This may take 30-60 seconds)
                    </>
                  ) : (
                    <>
                      <ImageIcon className="h-4 w-4 mr-2" />
                      Generate Image
                    </>
                  )}
                </Button>

                {generatedImage && (
                  <div className="mt-6 space-y-4" data-testid="generated-image-result">
                    <div className="border border-slate-700 rounded-lg overflow-hidden">
                      <img
                        src={generatedImage}
                        alt="Generated image"
                        className="w-full"
                      />
                    </div>

                    <Button
                      onClick={() => handleUseInEditor(generatedImage)}
                      className="w-full"
                      data-testid="use-image-in-editor-button"
                    >
                      <Wand2 className="h-4 w-4 mr-2" />
                      Use in Editor
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Info Section */}
        <Card className="mt-6 bg-slate-900/30 border-slate-800">
          <CardContent className="pt-6">
            <div className="flex items-start space-x-3">
              <Sparkles className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-white mb-2">Powered by Advanced AI</h4>
                <p className="text-sm text-slate-400">
                  We use state-of-the-art AI models including GPT-4 and DALL-E 3 to generate 
                  creative, high-quality memes. Each generation is unique and tailored to your input.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default AIGenerator;
