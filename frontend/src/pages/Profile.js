import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { uploadAPI } from '@/services/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { ArrowLeft, User, Settings, Crown, Upload } from 'lucide-react';

const Profile = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [uploading, setUploading] = useState(false);

  const handleAvatarUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const response = await uploadAPI.image(file);
      toast.success('Avatar updated!');
      // In a real app, you'd update the user profile here
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Failed to upload avatar');
    }
    setUploading(false);
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const getStorageLimit = (planType) => {
    const limits = {
      FREE: 100 * 1024 * 1024, // 100MB
      SOLO: 1024 * 1024 * 1024, // 1GB
      TEAM: 5 * 1024 * 1024 * 1024, // 5GB
      ENTERPRISE: 50 * 1024 * 1024 * 1024, // 50GB
    };
    return limits[planType] || limits.FREE;
  };

  const storageLimit = getStorageLimit(user?.plan_type);
  const storagePercentage = (user?.storage_used / storageLimit) * 100;

  return (
    <div className="min-h-screen bg-slate-950" data-testid="profile-page">
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

            <h1 className="text-2xl font-bold text-white">Profile & Settings</h1>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 max-w-4xl">
        <Tabs defaultValue="profile" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="profile" data-testid="tab-profile">
              <User className="h-4 w-4 mr-2" />
              Profile
            </TabsTrigger>
            <TabsTrigger value="account" data-testid="tab-account">
              <Settings className="h-4 w-4 mr-2" />
              Account
            </TabsTrigger>
            <TabsTrigger value="plan" data-testid="tab-plan">
              <Crown className="h-4 w-4 mr-2" />
              Plan
            </TabsTrigger>
          </TabsList>

          {/* Profile Tab */}
          <TabsContent value="profile" className="space-y-6">
            <Card className="bg-slate-900/50 border-slate-800">
              <CardHeader>
                <CardTitle>Profile Information</CardTitle>
                <CardDescription>Update your profile details</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Avatar */}
                <div className="flex items-center space-x-6">
                  <div className="relative">
                    {user?.avatar ? (
                      <img
                        src={user.avatar}
                        alt={user.username}
                        className="w-24 h-24 rounded-full object-cover"
                      />
                    ) : (
                      <div className="w-24 h-24 rounded-full bg-gradient-to-r from-green-500 to-blue-500 flex items-center justify-center text-white text-3xl font-bold">
                        {user?.username?.charAt(0).toUpperCase()}
                      </div>
                    )}
                    <label className="absolute bottom-0 right-0 bg-green-500 rounded-full p-2 cursor-pointer hover:bg-green-600 transition-colors">
                      <Upload className="h-4 w-4 text-white" />
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleAvatarUpload}
                        className="hidden"
                        disabled={uploading}
                      />
                    </label>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-white" data-testid="profile-username">
                      {user?.username}
                    </h3>
                    <p className="text-slate-400" data-testid="profile-email">{user?.email}</p>
                    <Badge className="mt-2" data-testid="profile-plan">{user?.plan_type}</Badge>
                  </div>
                </div>

                {/* User Stats */}
                <div className="grid grid-cols-3 gap-4">
                  <Card className="bg-slate-800/50 border-slate-700">
                    <CardContent className="pt-6">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-white">0</div>
                        <div className="text-sm text-slate-400">Memes Created</div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-slate-800/50 border-slate-700">
                    <CardContent className="pt-6">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-white">0</div>
                        <div className="text-sm text-slate-400">Templates</div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-slate-800/50 border-slate-700">
                    <CardContent className="pt-6">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-500">0</div>
                        <div className="text-sm text-slate-400">Total Views</div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </CardContent>
            </Card>

            {/* Storage Usage */}
            <Card className="bg-slate-900/50 border-slate-800">
              <CardHeader>
                <CardTitle>Storage Usage</CardTitle>
                <CardDescription>
                  {formatBytes(user?.storage_used || 0)} of {formatBytes(storageLimit)} used
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="w-full bg-slate-800 rounded-full h-4 overflow-hidden">
                  <div
                    className={`h-full transition-all ${
                      storagePercentage > 80 ? 'bg-red-500' : 'bg-green-500'
                    }`}
                    style={{ width: `${Math.min(storagePercentage, 100)}%` }}
                    data-testid="storage-bar"
                  />
                </div>
                <p className="text-sm text-slate-400 mt-2">
                  {storagePercentage.toFixed(1)}% of storage used
                </p>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Account Tab */}
          <TabsContent value="account" className="space-y-6">
            <Card className="bg-slate-900/50 border-slate-800">
              <CardHeader>
                <CardTitle>Account Settings</CardTitle>
                <CardDescription>Manage your account details</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="username">Username</Label>
                  <Input
                    id="username"
                    defaultValue={user?.username}
                    disabled
                    data-testid="username-input"
                  />
                  <p className="text-xs text-slate-400 mt-1">
                    Contact support to change your username
                  </p>
                </div>

                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    defaultValue={user?.email}
                    disabled
                    data-testid="email-input"
                  />
                  <p className="text-xs text-slate-400 mt-1">
                    Contact support to change your email
                  </p>
                </div>

                <div className="pt-4 border-t border-slate-700">
                  <Button
                    variant="destructive"
                    onClick={logout}
                    data-testid="logout-button"
                  >
                    Log Out
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Plan Tab */}
          <TabsContent value="plan" className="space-y-6">
            <Card className="bg-slate-900/50 border-slate-800">
              <CardHeader>
                <CardTitle>Current Plan</CardTitle>
                <CardDescription>You are on the {user?.plan_type} plan</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Plan Features */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between py-3 border-b border-slate-700">
                    <span className="text-white">Storage</span>
                    <span className="text-slate-400">{formatBytes(storageLimit)}</span>
                  </div>
                  <div className="flex items-center justify-between py-3 border-b border-slate-700">
                    <span className="text-white">AI Generations</span>
                    <span className="text-slate-400">
                      {user?.plan_type === 'FREE' ? '10/month' : 'Unlimited'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between py-3 border-b border-slate-700">
                    <span className="text-white">Team Members</span>
                    <span className="text-slate-400">
                      {user?.plan_type === 'FREE' ? '1' : user?.plan_type === 'SOLO' ? '1' : user?.plan_type === 'TEAM' ? '10' : 'Unlimited'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between py-3">
                    <span className="text-white">Priority Support</span>
                    <span className="text-slate-400">
                      {user?.plan_type === 'FREE' || user?.plan_type === 'SOLO' ? 'No' : 'Yes'}
                    </span>
                  </div>
                </div>

                {user?.plan_type === 'FREE' && (
                  <Button className="w-full" data-testid="upgrade-button">
                    <Crown className="h-4 w-4 mr-2" />
                    Upgrade Plan
                  </Button>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default Profile;
