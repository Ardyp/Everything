import React from 'react';
import { View, Text, ScrollView, RefreshControl } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { API_URL } from '../config';

interface SystemInfo {
  cpuUsage: number;
  memoryUsage: {
    total: number;
    used: number;
    free: number;
  };
  uptime: number;
}

export default function SystemInfoScreen() {
  const { data, isLoading, refetch } = useQuery<SystemInfo>({
    queryKey: ['systemInfo'],
    queryFn: async () => {
      const response = await fetch(`${API_URL}/system/info`);
      return response.json();
    }
  });

  const formatBytes = (bytes: number) => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    if (bytes === 0) return '0 Byte';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i)) + ' ' + sizes[i];
  };

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / (24 * 60 * 60));
    const hours = Math.floor((seconds % (24 * 60 * 60)) / (60 * 60));
    const minutes = Math.floor((seconds % (60 * 60)) / 60);
    return `${days}d ${hours}h ${minutes}m`;
  };

  return (
    <ScrollView 
      className="flex-1 bg-gray-100"
      refreshControl={
        <RefreshControl refreshing={isLoading} onRefresh={refetch} />
      }
    >
      <View className="p-4">
        <Text className="text-2xl font-bold mb-6">System Information</Text>
        
        {data ? (
          <View className="space-y-4">
            <View className="bg-white p-4 rounded-lg">
              <Text className="text-lg font-semibold">CPU Usage</Text>
              <Text className="text-3xl font-bold text-blue-600">{Math.round(data.cpuUsage)}%</Text>
            </View>

            <View className="bg-white p-4 rounded-lg">
              <Text className="text-lg font-semibold">Memory</Text>
              <View className="mt-2">
                <Text>Total: {formatBytes(data.memoryUsage.total)}</Text>
                <Text>Used: {formatBytes(data.memoryUsage.used)}</Text>
                <Text>Free: {formatBytes(data.memoryUsage.free)}</Text>
              </View>
            </View>

            <View className="bg-white p-4 rounded-lg">
              <Text className="text-lg font-semibold">System Uptime</Text>
              <Text className="text-xl">{formatUptime(data.uptime)}</Text>
            </View>
          </View>
        ) : (
          <Text className="text-center text-gray-500">
            {isLoading ? 'Loading...' : 'Failed to load system information'}
          </Text>
        )}
      </View>
    </ScrollView>
  );
} 