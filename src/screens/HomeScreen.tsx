import React from 'react';
import { View, Text, TouchableOpacity, ScrollView } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';

type RootStackParamList = {
  Home: undefined;
  SystemInfo: undefined;
  Processes: undefined;
  FileSystem: undefined;
};

type NavigationProp = NativeStackNavigationProp<RootStackParamList, 'Home'>;

export default function HomeScreen() {
  const navigation = useNavigation<NavigationProp>();

  const menuItems = [
    { title: 'System Information', route: 'SystemInfo', description: 'View system metrics and performance' },
    { title: 'Process Manager', route: 'Processes', description: 'Monitor and manage system processes' },
    { title: 'File System', route: 'FileSystem', description: 'Browse and manage files' },
  ];

  return (
    <ScrollView className="flex-1 bg-gray-100">
      <View className="p-4">
        <Text className="text-2xl font-bold mb-6">OS Manager</Text>
        <View className="space-y-4">
          {menuItems.map((item, index) => (
            <TouchableOpacity
              key={index}
              className="bg-white p-4 rounded-lg shadow-sm"
              onPress={() => navigation.navigate(item.route as keyof RootStackParamList)}
            >
              <Text className="text-lg font-semibold">{item.title}</Text>
              <Text className="text-gray-600 mt-1">{item.description}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>
    </ScrollView>
  );
} 