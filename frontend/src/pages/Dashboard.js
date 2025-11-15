import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { trendAPI } from '@/services/api';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Loader2, TrendingUp, Sparkles, Plus, User } from 'lucide-react';
import NotificationsPanel from '@/components/NotificationsPanel';

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedPlatform, setSelectedPlatform] = useState('all');

  useEffect(() => {
    loadTrends();
  }, [selectedPlatform]);

  const loadTrends = async () => {
    setLoading(true);
    try {
      const params = selectedPlatform !== 'all' ? { platform: selectedPlatform } : {};
      const response = await trendAPI.list(params);
      setTrends(response.data);
    } catch (error) {
      console.error('Failed to load trends:', error);
    }
    setLoading(false);
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-500';
    if (score >= 60) return 'text-yellow-500';
    return 'text-orange-500';
  };

  const getPlatformBadgeColor = (platform) => {
    switch (platform) {
      case 'TWITTER':
        return 'bg-blue-500';
      case 'REDDIT':
        return 'bg-orange-500';
      case 'INSTAGRAM':
        return 'bg-pink-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="min-h-screen bg-bg-darker" data-testid="dashboard-page">
      {/* Header */}
      <header className="border-b border-slate-800 bg-bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-primary-green to-primary-blue">
              MemeCraft Pro
            </h1>
            <Badge variant="secondary" className="hidden md:inline-flex">
              {user?.plan_type || 'FREE'}
            </Badge>
          </div>

          <div className="flex items-center space-x-4">
            <Button
              onClick={() => navigate('/editor/new')}
              className="bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600"
              data-testid="create-new-button"
            >
              <Plus className="h-4 w-4 mr-2" />
              Create New
            </Button>

            <Button
              variant="outline"
              onClick={() => navigate('/memes')}
              data-testid="my-memes-button"
            >
              My Memes
            </Button>

            <NotificationsPanel />

            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/profile')}
              data-testid="profile-button"
            >
              <User className="h-5 w-5" />
            </Button>

            <div className="flex items-center space-x-2">
              <div className="text-right">
                <p className="text-sm font-medium cursor-pointer hover:text-green-400" onClick={() => navigate('/profile')} data-testid="user-username">{user?.username}</p>
                <p className="text-xs text-muted-foreground">{user?.email}</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold mb-2 text-white">
            Welcome back, {user?.username}! 👋
          </h2>
          <p className="text-slate-400">
            Discover trending memes and create your own viral content with AI
          </p>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <Card 
            className="cursor-pointer hover:border-green-500 transition-colors bg-slate-900/50 border-slate-800"
            onClick={() => navigate('/editor/new')}
            data-testid="quick-action-create"
          >
            <CardContent className="pt-6">
              <div className="flex items-center space-x-4">
                <div className="p-3 rounded-full bg-green-500/10">
                  <Plus className="h-6 w-6 text-green-500" />
                </div>
                <div>
                  <h3 className="font-semibold text-white">Create Meme</h3>
                  <p className="text-sm text-slate-400">Start with canvas</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card 
            className="cursor-pointer hover:border-blue-500 transition-colors bg-slate-900/50 border-slate-800"
            onClick={() => navigate('/ai-generate')}
            data-testid="quick-action-ai"
          >
            <CardContent className="pt-6">
              <div className="flex items-center space-x-4">
                <div className="p-3 rounded-full bg-blue-500/10">
                  <Sparkles className="h-6 w-6 text-blue-500" />
                </div>
                <div>
                  <h3 className="font-semibold text-white">AI Generator</h3>
                  <p className="text-sm text-slate-400">AI creates for you</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card 
            className="cursor-pointer hover:border-purple-500 transition-colors bg-slate-900/50 border-slate-800"
            onClick={() => navigate('/templates')}
            data-testid="quick-action-templates"
          >
            <CardContent className="pt-6">
              <div className="flex items-center space-x-4">
                <div className="p-3 rounded-full bg-purple-500/10">
                  <TrendingUp className="h-6 w-6 text-purple-500" />
                </div>
                <div>
                  <h3 className="font-semibold text-white">Templates</h3>
                  <p className="text-sm text-slate-400">Use popular formats</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card 
            className="cursor-pointer hover:border-orange-500 transition-colors bg-slate-900/50 border-slate-800"
            onClick={() => navigate('/gif-creator')}
            data-testid="quick-action-gif"
          >
            <CardContent className="pt-6">
              <div className="flex items-center space-x-4">
                <div className="p-3 rounded-full bg-orange-500/10">
                  <svg className="h-6 w-6 text-orange-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-white">GIF Creator</h3>
                  <p className="text-sm text-slate-400">Animated memes</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Trending Memes */}
        <Card className="bg-slate-900/50 border-slate-800">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-2xl text-white flex items-center">
                  <TrendingUp className="h-6 w-6 mr-2 text-green-500" />
                  Trending Memes
                </CardTitle>
                <CardDescription>Most viral content right now</CardDescription>
              </div>

              <Tabs value={selectedPlatform} onValueChange={setSelectedPlatform}>
                <TabsList>
                  <TabsTrigger value="all" data-testid="platform-all">All</TabsTrigger>
                  <TabsTrigger value="TWITTER" data-testid="platform-twitter">Twitter</TabsTrigger>
                  <TabsTrigger value="REDDIT" data-testid="platform-reddit">Reddit</TabsTrigger>
                </TabsList>
              </Tabs>
            </div>
          </CardHeader>

          <CardContent>
            {loading ? (
              <div className="flex items-center justify-center py-12" data-testid="trends-loading">
                <Loader2 className="h-8 w-8 animate-spin text-green-500" />
              </div>
            ) : trends.length === 0 ? (
              <div className="text-center py-12 text-slate-400" data-testid="trends-empty">
                No trends available at the moment
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {trends.map((trend) => (
                  <Card 
                    key={trend.id}
                    className="cursor-pointer hover:border-green-500 transition-colors bg-slate-800/50 border-slate-700 overflow-hidden group"
                    onClick={() => navigate(`/editor/new?trendId=${trend.id}`)}
                    data-testid={`trend-card-${trend.id}`}
                  >
                    <div className="aspect-video relative overflow-hidden">
                      <img
                        src={trend.image_url}
                        alt={trend.title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                      />
                      <Badge 
                        className={`absolute top-2 right-2 ${getPlatformBadgeColor(trend.platform)}`}
                        data-testid={`trend-platform-${trend.id}`}
                      >
                        {trend.platform}
                      </Badge>
                    </div>

                    <CardContent className="p-4">
                      <h3 className="font-semibold text-white mb-2 line-clamp-2" data-testid={`trend-title-${trend.id}`}>
                        {trend.title}
                      </h3>
                      
                      <p className="text-sm text-slate-400 mb-3 line-clamp-2">
                        {trend.description}
                      </p>

                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <span className="text-2xl">🔥</span>
                          <span className={`text-xl font-bold ${getScoreColor(trend.viral_score)}`} data-testid={`trend-score-${trend.id}`}>
                            {trend.viral_score}%
                          </span>
                        </div>

                        <Button size="sm" variant="ghost" data-testid={`trend-use-button-${trend.id}`}>
                          Use Template →
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default Dashboard;
