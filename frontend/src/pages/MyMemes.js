import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { memeAPI } from '@/services/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { toast } from 'sonner';
import {
  Plus,
  Search,
  MoreVertical,
  Edit,
  Copy,
  Trash2,
  ArrowLeft,
  Loader2,
} from 'lucide-react';

const MyMemes = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [memes, setMemes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadMemes();
  }, []);

  const loadMemes = async () => {
    setLoading(true);
    try {
      const response = await memeAPI.list();
      setMemes(response.data);
    } catch (error) {
      console.error('Failed to load memes:', error);
      toast.error('Failed to load memes');
    }
    setLoading(false);
  };

  const handleEdit = (memeId) => {
    navigate(`/editor/${memeId}`);
  };

  const handleDuplicate = async (memeId) => {
    try {
      toast.loading('Duplicating meme...');
      const response = await memeAPI.duplicate(memeId);
      toast.success('Meme duplicated!');
      loadMemes();
    } catch (error) {
      console.error('Duplicate error:', error);
      toast.error('Failed to duplicate meme');
    }
  };

  const handleDelete = async (memeId) => {
    if (!window.confirm('Are you sure you want to delete this meme?')) return;

    try {
      await memeAPI.delete(memeId);
      toast.success('Meme deleted');
      setMemes(memes.filter((m) => m.id !== memeId));
    } catch (error) {
      console.error('Delete error:', error);
      toast.error('Failed to delete meme');
    }
  };

  const filteredMemes = memes.filter((meme) =>
    meme.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-slate-950" data-testid="my-memes-page">
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

              <h1 className="text-2xl font-bold text-white">My Memes</h1>
            </div>

            <Button
              onClick={() => navigate('/editor/new')}
              className="bg-gradient-to-r from-green-500 to-blue-500"
              data-testid="create-new-button"
            >
              <Plus className="h-4 w-4 mr-2" />
              Create New
            </Button>
          </div>

          <div className="mt-4 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
            <Input
              placeholder="Search memes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
              data-testid="search-input"
            />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {loading ? (
          <div className="flex items-center justify-center py-12" data-testid="memes-loading">
            <Loader2 className="h-8 w-8 animate-spin text-green-500" />
          </div>
        ) : filteredMemes.length === 0 ? (
          <div className="text-center py-12" data-testid="memes-empty">
            <div className="text-6xl mb-4">🎨</div>
            <h3 className="text-xl font-semibold text-white mb-2">
              {searchQuery ? 'No memes found' : 'No memes yet'}
            </h3>
            <p className="text-slate-400 mb-6">
              {searchQuery
                ? 'Try a different search term'
                : 'Create your first meme to get started'}
            </p>
            {!searchQuery && (
              <Button onClick={() => navigate('/editor/new')} data-testid="create-first-button">
                <Plus className="h-4 w-4 mr-2" />
                Create Meme
              </Button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filteredMemes.map((meme) => (
              <Card
                key={meme.id}
                className="bg-slate-900/50 border-slate-800 overflow-hidden group hover:border-green-500 transition-colors"
                data-testid={`meme-card-${meme.id}`}
              >
                <div
                  className="aspect-video relative cursor-pointer"
                  onClick={() => handleEdit(meme.id)}
                >
                  {meme.thumbnail_url ? (
                    <img
                      src={meme.thumbnail_url}
                      alt={meme.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center bg-slate-800">
                      <span className="text-4xl">🎭</span>
                    </div>
                  )}
                </div>

                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h3
                        className="font-semibold text-white truncate cursor-pointer hover:text-green-400"
                        onClick={() => handleEdit(meme.id)}
                        data-testid={`meme-title-${meme.id}`}
                      >
                        {meme.title}
                      </h3>
                      <p className="text-xs text-slate-400 mt-1">
                        {new Date(meme.created_at).toLocaleDateString()}
                      </p>
                    </div>

                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 w-8 p-0"
                          data-testid={`meme-menu-${meme.id}`}
                        >
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem
                          onClick={() => handleEdit(meme.id)}
                          data-testid={`meme-edit-${meme.id}`}
                        >
                          <Edit className="h-4 w-4 mr-2" />
                          Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() => handleDuplicate(meme.id)}
                          data-testid={`meme-duplicate-${meme.id}`}
                        >
                          <Copy className="h-4 w-4 mr-2" />
                          Duplicate
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() => handleDelete(meme.id)}
                          className="text-red-500"
                          data-testid={`meme-delete-${meme.id}`}
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
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

export default MyMemes;
