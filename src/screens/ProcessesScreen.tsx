import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, FlatList } from 'react-native';
import { useQuery } from '@tanstack/react-query';

interface Process {
  pid: number;
  name: string;
  cpu_percent: number;
  memory_percent: number;
  status: string;
}

export default function ProcessesScreen() {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'cpu' | 'memory'>('cpu');

  const { data, isLoading, refetch } = useQuery<Process[]>({
    queryKey: ['processes'],
    queryFn: async () => {
      const response = await fetch('http://localhost:8000/processes');
      return response.json();
    },
    refetchInterval: 5000 // Refresh every 5 seconds
  });

  const filteredProcesses = data?.filter(process => 
    process.name.toLowerCase().includes(searchTerm.toLowerCase())
  ).sort((a, b) => 
    sortBy === 'cpu' 
      ? b.cpu_percent - a.cpu_percent 
      : b.memory_percent - a.memory_percent
  );

  const renderProcess = ({ item }: { item: Process }) => (
    <View className="bg-white p-4 rounded-lg mb-2 flex-row justify-between items-center">
      <View>
        <Text className="font-semibold">{item.name}</Text>
        <Text className="text-gray-500">PID: {item.pid}</Text>
      </View>
      <View className="items-end">
        <Text>CPU: {item.cpu_percent.toFixed(1)}%</Text>
        <Text>Memory: {item.memory_percent.toFixed(1)}%</Text>
      </View>
    </View>
  );

  return (
    <View className="flex-1 bg-gray-100">
      <View className="p-4">
        <TextInput
          className="bg-white p-3 rounded-lg mb-4"
          placeholder="Search processes..."
          value={searchTerm}
          onChangeText={setSearchTerm}
        />

        <View className="flex-row justify-around mb-4">
          <TouchableOpacity 
            className={`px-4 py-2 rounded-lg ${sortBy === 'cpu' ? 'bg-blue-500' : 'bg-gray-300'}`}
            onPress={() => setSortBy('cpu')}
          >
            <Text className={sortBy === 'cpu' ? 'text-white' : 'text-gray-700'}>Sort by CPU</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            className={`px-4 py-2 rounded-lg ${sortBy === 'memory' ? 'bg-blue-500' : 'bg-gray-300'}`}
            onPress={() => setSortBy('memory')}
          >
            <Text className={sortBy === 'memory' ? 'text-white' : 'text-gray-700'}>Sort by Memory</Text>
          </TouchableOpacity>
        </View>

        {isLoading ? (
          <Text className="text-center text-gray-500">Loading processes...</Text>
        ) : (
          <FlatList
            data={filteredProcesses}
            renderItem={renderProcess}
            keyExtractor={item => item.pid.toString()}
            onRefresh={refetch}
            refreshing={isLoading}
          />
        )}
      </View>
    </View>
  );
} 