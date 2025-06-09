import React, { useState } from 'react';
import { View, Text, TouchableOpacity, FlatList, Switch } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { API_URL } from '../config';

interface FileItem {
  name: string;
  path: string;
  type: 'file' | 'directory';
  size: number;
  modified: string;
}

export default function FileSystemScreen() {
  const [currentPath, setCurrentPath] = useState('');
  const [showHidden, setShowHidden] = useState(false);

  const { data, isLoading, refetch } = useQuery<FileItem[]>({
    queryKey: ['files', currentPath],
    queryFn: async () => {
      const response = await fetch(`${API_URL}/files?path=${encodeURIComponent(currentPath)}&show_hidden=${showHidden}`);
      return response.json();
    }
  });

  const formatSize = (size: number) => {
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let index = 0;
    while (size >= 1024 && index < units.length - 1) {
      size /= 1024;
      index++;
    }
    return `${size.toFixed(1)} ${units[index]}`;
  };

  const navigateToDirectory = (path: string) => {
    setCurrentPath(path);
  };

  const goBack = () => {
    const parentPath = currentPath.split('/').slice(0, -1).join('/');
    setCurrentPath(parentPath);
  };

  const renderItem = ({ item }: { item: FileItem }) => (
    <TouchableOpacity
      className="bg-white p-4 rounded-lg mb-2 flex-row justify-between items-center"
      onPress={() => item.type === 'directory' && navigateToDirectory(item.path)}
    >
      <View className="flex-1">
        <Text className="font-semibold">{item.name}</Text>
        <Text className="text-gray-500 text-sm">
          {item.type === 'file' ? formatSize(item.size) : 'Directory'}
        </Text>
      </View>
      <Text className="text-gray-500 text-sm">{new Date(item.modified).toLocaleDateString()}</Text>
    </TouchableOpacity>
  );

  return (
    <View className="flex-1 bg-gray-100">
      <View className="p-4">
        {/* Path and Back Button */}
        <View className="flex-row items-center justify-between mb-4">
          {currentPath && (
            <TouchableOpacity 
              className="bg-blue-500 px-4 py-2 rounded-lg"
              onPress={goBack}
            >
              <Text className="text-white">Back</Text>
            </TouchableOpacity>
          )}
          <Text className="flex-1 ml-2" numberOfLines={1}>
            {currentPath || 'Root Directory'}
          </Text>
        </View>

        {/* Show Hidden Files Toggle */}
        <View className="flex-row items-center justify-end mb-4">
          <Text className="mr-2">Show Hidden Files</Text>
          <Switch
            value={showHidden}
            onValueChange={setShowHidden}
          />
        </View>

        {/* File List */}
        {isLoading ? (
          <Text className="text-center text-gray-500">Loading files...</Text>
        ) : (
          <FlatList
            data={data}
            renderItem={renderItem}
            keyExtractor={item => item.path}
            onRefresh={refetch}
            refreshing={isLoading}
          />
        )}
      </View>
    </View>
  );
} 