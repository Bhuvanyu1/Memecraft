import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { templateAPI } from '@/services/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import { ArrowLeft, Loader2, ThumbsUp } from 'lucide-react';

const Templates = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    loadCategories();
    loadTemplates();
  }, [selectedCategory]);

  const loadCategories = async () => {
    try {
      const response = await templateAPI.categories();
      setCategories(['all', ...response.data.categories]);
    } catch (error) {
      console.error('Failed to load categories:', error);
    }
  };

  const loadTemplates = async () => {
    setLoading(true);
    try {
      const params = selectedCategory !== 'all' ? { category: selectedCategory } : {};
      const response = await templateAPI.list(params);
      setTemplates(response.data);
    } catch (error) {
      console.error('Failed to load templates:', error);
      toast.error('Failed to load templates');
    }
    setLoading(false);
  };

  const handleUseTemplate = (templateId) => {
    navigate(`/editor/new?templateId=${templateId}`);
  };

  const handleVote = async (templateId, vote) => {
    try {
      await templateAPI.vote(templateId, vote);
      toast.success('Vote recorded!');
      loadTemplates();
    } catch (error) {
      console.error('Vote error:', error);
      toast.error('Failed to vote');
    }
  };

  return (
    <div className="min-h-screen bg-slate-950" data-testid="templates-page">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
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

              <h1 className="text-2xl font-bold text-white">Template Library</h1>
            </div>
          </div>

          {/* Category Tabs */}
          <div className="mt-4 overflow-x-auto">
            <div className="flex space-x-2 pb-2">
              {categories.map((category) => (
                <Button
                  key={category}
                  variant={selectedCategory === category ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedCategory(category)}
                  data-testid={`category-${category}`}
                >
                  {category === 'all' ? 'All' : category}
                </Button>
              ))}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {loading ? (
          <div className="flex items-center justify-center py-12" data-testid="templates-loading">
            <Loader2 className="h-8 w-8 animate-spin text-green-500" />
          </div>
        ) : templates.length === 0 ? (
          <div className="text-center py-12 text-slate-400" data-testid="templates-empty">
            No templates found in this category
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {templates.map((template) => (
              <Card
                key={template.id}
                className="bg-slate-900/50 border-slate-800 overflow-hidden group hover:border-green-500 transition-colors"
                data-testid={`template-card-${template.id}`}
              >
                <div
                  className="aspect-video relative cursor-pointer"
                  onClick={() => handleUseTemplate(template.id)}
                >
                  <img
                    src={template.image_url}
                    alt={template.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                  />
                  {template.is_community && (
                    <Badge className="absolute top-2 right-2 bg-purple-500">
                      Community
                    </Badge>
                  )}
                </div>

                <CardContent className="p-4">
                  <h3
                    className="font-semibold text-white mb-2 line-clamp-2 cursor-pointer hover:text-green-400"
                    onClick={() => handleUseTemplate(template.id)}
                    data-testid={`template-title-${template.id}`}
                  >
                    {template.title}
                  </h3>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2 text-sm text-slate-400">
                      <ThumbsUp className="h-4 w-4" />
                      <span data-testid={`template-votes-${template.id}`}>{template.votes}</span>
                    </div>

                    <Button
                      size="sm"
                      onClick={() => handleUseTemplate(template.id)}
                      data-testid={`template-use-${template.id}`}
                    >
                      Use Template
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default Templates;
